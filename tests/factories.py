from __future__ import annotations

from datetime import date

from uk_election_data.general.constituencies.candidate import Candidate, VotesReceived
from uk_election_data.general.constituencies.constituency import Constituency


DEFAULT_ELECTION_DATE = date(2024, 7, 4)


def make_candidate(
    name: str,
    party: str,
    votes: int,
    place: int,
    *,
    elected: bool = False,
    candidacy_id: int | None = None,
    constituency_id: int = 1,
    election_id: int = 100,
    constituency: str = "Test Constituency",
    election_date: date = DEFAULT_ELECTION_DATE,
    share: float = 0.0,
) -> Candidate:
    if candidacy_id is None:
        candidacy_id = place

    return Candidate(
        candidacy_id=candidacy_id,
        constituency_id=constituency_id,
        election_id=election_id,
        name=name,
        party=party,
        constituency=constituency,
        election_date=election_date,
        elected=elected,
        votes=VotesReceived(total=votes, share=share, place=place),
    )


def make_constituency(
    candidates: list[Candidate],
    *,
    constituency_id: int = 1,
    election_id: int = 100,
    name: str = "Test Constituency",
    country: str = "England",
    region: str | None = "North West",
    election_date: date = DEFAULT_ELECTION_DATE,
    invalid_votes: int = 20,
    registered_voters: int = 3000,
) -> Constituency:
    return Constituency(
        constituency_id=constituency_id,
        election_id=election_id,
        name=name,
        country=country,
        region=region,
        election_date=election_date,
        total_invalid_votes=invalid_votes,
        total_registered_voters=registered_voters,
        candidate_list=candidates,
    )
