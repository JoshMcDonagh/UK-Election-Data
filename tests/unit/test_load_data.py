from datetime import date

from uk_election_data._load_data import _get_constituency_rows, _load_constituency


def _row(
    *,
    election_id=101,
    constituency_id=1,
    constituency_name="Example Central",
    country="England",
    region="London",
    invalid_votes=20,
    registered_voters=50_000,
    candidacy_id=1,
    given_name="Jane",
    family_name="Example",
    independent=0,
    speaker=0,
    vote_count=20_000,
    vote_share=0.5,
    result_position=1,
    winner=1,
    parties="Example Party",
):
    return {
        "election_id": election_id,
        "constituency_id": constituency_id,
        "constituency_name": constituency_name,
        "country": country,
        "region": region,
        "total_invalid_votes": invalid_votes,
        "total_registered_voters": registered_voters,
        "candidacy_id": candidacy_id,
        "candidate_given_name": given_name,
        "candidate_family_name": family_name,
        "is_standing_as_independent": independent,
        "is_standing_as_commons_speaker": speaker,
        "vote_count": vote_count,
        "vote_share": vote_share,
        "result_position": result_position,
        "is_winning_candidacy": winner,
        "parties": parties,
    }


def test_get_constituency_rows_groups_rows_by_election_id():
    row_a = _row(election_id=10, candidacy_id=1)
    row_b = _row(election_id=10, candidacy_id=2)
    row_c = _row(election_id=20, candidacy_id=3)

    result = _get_constituency_rows([row_a, row_b, row_c])  # type: ignore[arg-type]

    assert result == {
        10: [row_a, row_b],
        20: [row_c],
    }


def test_get_constituency_rows_handles_empty_input():
    assert _get_constituency_rows([]) == {}


def test_load_constituency_maps_metadata_and_candidates():
    rows = [
        _row(
            candidacy_id=1,
            given_name="Jane",
            family_name="Winner",
            vote_count=20_000,
            vote_share=0.50,
            result_position=1,
            winner=1,
            parties="Party A",
        ),
        _row(
            candidacy_id=2,
            given_name="John",
            family_name="Runner-up",
            vote_count=15_000,
            vote_share=0.375,
            result_position=2,
            winner=0,
            parties="Party B",
        ),
    ]

    constituency = _load_constituency(date(2024, 7, 4), 101, rows)  # type: ignore[arg-type]

    assert constituency.constituency_id == 1
    assert constituency.election_id == 101
    assert constituency.name == "Example Central"
    assert constituency.country == "England"
    assert constituency.region == "London"
    assert constituency.election_date == date(2024, 7, 4)
    assert constituency.total_invalid_votes == 20
    assert constituency.total_registered_voters == 50_000
    assert constituency.total_valid_votes == 35_000
    assert constituency.elected_candidate == "Jane Winner"
    assert constituency.winning_party == "Party A"

    winner = constituency.get_candidate_by_name("Jane Winner")
    assert winner.candidacy_id == 1
    assert winner.elected is True
    assert winner.votes.total == 20_000
    assert winner.votes.share == 0.50
    assert winner.votes.place == 1


def test_load_constituency_normalises_independent_party():
    rows = [
        _row(independent=1, parties=None, winner=1),
        _row(
            candidacy_id=2,
            given_name="Other",
            family_name="Candidate",
            vote_count=10_000,
            vote_share=0.25,
            result_position=2,
            winner=0,
            parties="Party A",
        ),
    ]

    constituency = _load_constituency(date(2024, 7, 4), 101, rows)  # type: ignore[arg-type]

    assert constituency.get_candidate_by_name("Jane Example").party == "Independent"
    assert constituency.winning_party == "Independent"


def test_load_constituency_normalises_commons_speaker_party():
    rows = [
        _row(speaker=1, parties=None, winner=1),
        _row(
            candidacy_id=2,
            given_name="Other",
            family_name="Candidate",
            vote_count=10_000,
            vote_share=0.25,
            result_position=2,
            winner=0,
            parties="Party A",
        ),
    ]

    constituency = _load_constituency(date(2024, 7, 4), 101, rows)  # type: ignore[arg-type]

    assert constituency.get_candidate_by_name("Jane Example").party == "Speaker"
    assert constituency.winning_party == "Speaker"


def test_independent_takes_precedence_over_speaker_flag():
    rows = [
        _row(independent=1, speaker=1, parties="Party A", winner=1),
        _row(
            candidacy_id=2,
            given_name="Other",
            family_name="Candidate",
            vote_count=10_000,
            vote_share=0.25,
            result_position=2,
            winner=0,
            parties="Party B",
        ),
    ]

    constituency = _load_constituency(date(2024, 7, 4), 101, rows)  # type: ignore[arg-type]

    assert constituency.winning_party == "Independent"


def test_load_constituency_strips_candidate_name_whitespace():
    rows = [
        _row(given_name=" Jane ", family_name=" Winner ", winner=1),
        _row(
            candidacy_id=2,
            given_name="Bob",
            family_name="Other",
            vote_count=10_000,
            vote_share=0.25,
            result_position=2,
            winner=0,
            parties="Party B",
        ),
    ]

    constituency = _load_constituency(date(2024, 7, 4), 101, rows)  # type: ignore[arg-type]

    # The outer whitespace is stripped. Internal whitespace reflects the source fields.
    assert constituency.elected_candidate == "Jane   Winner"


def test_load_constituency_converts_database_winner_flag_to_bool():
    rows = [
        _row(winner=1),
        _row(
            candidacy_id=2,
            given_name="Bob",
            family_name="Other",
            vote_count=10_000,
            vote_share=0.25,
            result_position=2,
            winner=0,
            parties="Party B",
        ),
    ]

    constituency = _load_constituency(date(2024, 7, 4), 101, rows)  # type: ignore[arg-type]

    assert constituency.candidate_list[0].elected is True
    assert constituency.candidate_list[1].elected is False
