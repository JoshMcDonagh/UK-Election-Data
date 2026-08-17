import sqlite3
from datetime import date
from importlib.resources import files

from uk_election_data.general.constituencies import Constituencies, Constituency
from uk_election_data.general.constituencies.candidate import Candidate, VotesReceived
from uk_election_data.general.election_result import GeneralElection


def _connect() -> sqlite3.Connection:
    db_path = files("uk_election_data").joinpath("data/psephology.db")

    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    return connection


def get_general_election_dates(include_notional: bool = False) -> list[date]:
    with _connect() as connection:
        if include_notional:
            rows = connection.execute(
                """
                SELECT polling_on
                FROM general_elections
                WHERE is_notional = 1
                ORDER BY polling_on
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT polling_on
                FROM general_elections
                ORDER BY polling_on
                """
            ).fetchall()

        return [
            date.fromisoformat(row["polling_on"])
            for row in rows
        ]


def _get_rows(connection: sqlite3.Connection, general_election_id) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT e.id AS election_id,

            ca.id AS constituency_id,
            cg.name AS constituency_name,
            country.name AS country,
            region.name AS region,
            
            e.invalid_vote_count AS total_invalid_votes,
            electorate.population_count AS total_registered_voters,

            cand.id AS candidacy_id,
            cand.candidate_given_name,
            cand.candidate_family_name,
            cand.is_standing_as_independent,
            cand.is_standing_as_commons_speaker,
            cand.vote_count,
            cand.vote_share,
            cand.result_position,
            cand.is_winning_candidacy,

            GROUP_CONCAT(pp.name, ' / ') AS parties

        FROM elections e

        JOIN constituency_groups cg
            ON cg.id = e.constituency_group_id

        JOIN constituency_areas ca
            ON ca.id = cg.constituency_area_id

        JOIN countries country
            ON country.id = ca.country_id

        LEFT JOIN english_regions region
            ON region.id = ca.english_region_id
        
        JOIN electorates electorate
            ON electorate.id = e.electorate_id

        JOIN candidacies cand
            ON cand.election_id = e.id

        LEFT JOIN certifications cert
            ON cert.candidacy_id = cand.id

        LEFT JOIN political_parties pp
            ON pp.id = cert.political_party_id

        WHERE e.general_election_id = ?

        GROUP BY cand.id

        ORDER BY cg.name,
                 cand.result_position
        """,
        (general_election_id,),
    ).fetchall()


def _get_constituency_rows(rows: list[sqlite3.Row]) -> dict[int, list[sqlite3.Row]]:
    constituency_rows: dict[int, list[sqlite3.Row]] = {}

    for row in rows:
        election_id = row["election_id"]

        if election_id not in constituency_rows:
            constituency_rows[election_id] = []

        constituency_rows[election_id].append(row)

    return constituency_rows


def _load_constituency(election_date: date, election_id: int, candidate_rows: list[sqlite3.Row]) -> Constituency:
    first_row = candidate_rows[0]

    candidate_list: list[Candidate] = []

    for row in candidate_rows:
        if row["is_standing_as_independent"]:
            party = "Independent"
        elif row["is_standing_as_commons_speaker"]:
            party = "Speaker"
        else:
            party = row["parties"]

        candidate_name = (
            f"{row['candidate_given_name']} "
            f"{row['candidate_family_name']}"
        ).strip()

        candidate_list.append(
            Candidate(
                candidacy_id=row["candidacy_id"],
                constituency_id=row["constituency_id"],
                election_id=row["election_id"],
                name=candidate_name,
                party=party,
                constituency=first_row["constituency_name"],
                election_date=election_date,
                elected=bool(row["is_winning_candidacy"]),
                votes=VotesReceived(
                    total=row["vote_count"],
                    share=row["vote_share"],
                    place=row["result_position"],
                ),
            )
        )

    return Constituency(
        constituency_id=first_row["constituency_id"],
        election_id=election_id,
        name=first_row["constituency_name"],
        country=first_row["country"],
        region=first_row["region"],
        election_date=election_date,
        total_invalid_votes=first_row["total_invalid_votes"],
        total_registered_voters=first_row["total_registered_voters"],
        candidate_list=candidate_list,
    )


def load_general_election_result(election_date: date, is_notional: bool = False) -> GeneralElection:
    with _connect() as connection:
        general_election = connection.execute(
            """
            SELECT id
            FROM general_elections
            WHERE polling_on = ?
              AND is_notional = ?
            """,
            (election_date.isoformat(), int(is_notional)),
        ).fetchone()

        if general_election is None:
            raise ValueError(f"No general election found for {election_date}")

        general_election_id = general_election["id"]

        rows = _get_rows(connection, general_election_id)

        constituency_rows = _get_constituency_rows(rows)

        constituency_list: list[Constituency] = []
        for election_id, candidate_rows in constituency_rows.items():
            constituency_list.append(_load_constituency(election_date, election_id, candidate_rows))

        return GeneralElection(general_election_id, election_date, is_notional, Constituencies(constituency_list))



