from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from uk_election_data.general.constituencies.candidate import Candidate, VotesReceived


def test_votes_received_stores_values():
    votes = VotesReceived(total=12_345, share=0.42, place=2)

    assert votes.total == 12_345
    assert votes.share == 0.42
    assert votes.place == 2


def test_candidate_stores_values():
    votes = VotesReceived(total=20_000, share=0.51, place=1)
    candidate = Candidate(
        candidacy_id=10,
        constituency_id=20,
        election_id=30,
        name="Jane Example",
        party="Example Party",
        constituency="Example Central",
        election_date=date(2024, 7, 4),
        elected=True,
        votes=votes,
    )

    assert candidate.candidacy_id == 10
    assert candidate.constituency_id == 20
    assert candidate.election_id == 30
    assert candidate.name == "Jane Example"
    assert candidate.party == "Example Party"
    assert candidate.constituency == "Example Central"
    assert candidate.election_date == date(2024, 7, 4)
    assert candidate.elected is True
    assert candidate.votes is votes


def test_votes_received_is_immutable():
    votes = VotesReceived(total=100, share=0.5, place=1)

    with pytest.raises(FrozenInstanceError):
        votes.total = 200  # type: ignore[misc]


def test_candidate_is_immutable():
    candidate = Candidate(
        candidacy_id=1,
        constituency_id=2,
        election_id=3,
        name="Jane Example",
        party="Example Party",
        constituency="Example Central",
        election_date=date(2024, 7, 4),
        elected=True,
        votes=VotesReceived(total=100, share=0.5, place=1),
    )

    with pytest.raises(FrozenInstanceError):
        candidate.name = "Different Name"  # type: ignore[misc]
