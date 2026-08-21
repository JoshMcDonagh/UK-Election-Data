from datetime import date

import pytest

from tests.factories import make_candidate, make_constituency


def _standard_candidates():
    return [
        make_candidate("Alice Winner", "Party A", 1_000, 1, elected=True, share=0.50),
        make_candidate("Bob Runner-up", "Party B", 750, 2, share=0.375),
        make_candidate("Charlie Independent", "Independent", 250, 3, share=0.125),
    ]


def test_constituency_stores_metadata():
    constituency = make_constituency(
        _standard_candidates(),
        constituency_id=42,
        election_id=99,
        name="Example Central",
        country="England",
        region="London",
        election_date=date(2024, 7, 4),
        invalid_votes=21,
        registered_voters=3_000,
    )

    assert constituency.constituency_id == 42
    assert constituency.election_id == 99
    assert constituency.name == "Example Central"
    assert constituency.country == "England"
    assert constituency.region == "London"
    assert constituency.election_date == date(2024, 7, 4)
    assert constituency.total_invalid_votes == 21
    assert constituency.total_registered_voters == 3_000


def test_constituency_accepts_none_region():
    constituency = make_constituency(_standard_candidates(), region=None)

    assert constituency.region is None


def test_constituency_calculates_vote_totals_and_turnout():
    constituency = make_constituency(
        _standard_candidates(),
        invalid_votes=20,
        registered_voters=3_000,
    )

    assert constituency.total_valid_votes == 2_000
    assert constituency.total_invalid_votes == 20
    assert constituency.total_votes == 2_020
    assert constituency.turnout == pytest.approx(2_020 / 3_000)


def test_constituency_identifies_winner():
    constituency = make_constituency(_standard_candidates())

    assert constituency.elected_candidate == "Alice Winner"
    assert constituency.winning_party == "Party A"


def test_constituency_rejects_no_winner():
    candidates = [
        make_candidate("Alice", "Party A", 1_000, 1),
        make_candidate("Bob", "Party B", 900, 2),
    ]

    with pytest.raises(ValueError, match="found none"):
        make_constituency(candidates)


def test_constituency_rejects_multiple_winners():
    candidates = [
        make_candidate("Alice", "Party A", 1_000, 1, elected=True),
        make_candidate("Bob", "Party B", 900, 2, elected=True),
    ]

    with pytest.raises(ValueError, match="more than one"):
        make_constituency(candidates)


def test_constituency_copies_candidate_list_on_input():
    candidates = _standard_candidates()
    constituency = make_constituency(candidates)

    candidates.clear()

    assert len(constituency.candidate_list) == 3


def test_candidate_list_property_returns_defensive_copy():
    constituency = make_constituency(_standard_candidates())

    returned = constituency.candidate_list
    returned.clear()

    assert len(constituency.candidate_list) == 3


def test_get_candidate_by_name():
    constituency = make_constituency(_standard_candidates())

    candidate = constituency.get_candidate_by_name("Bob Runner-up")

    assert candidate.party == "Party B"
    assert candidate.votes.total == 750


def test_get_candidate_by_place():
    constituency = make_constituency(_standard_candidates())

    candidate = constituency.get_candidate_by_place(3)

    assert candidate.name == "Charlie Independent"


def test_get_candidate_by_party_returns_all_matching_candidates():
    candidates = [
        make_candidate("Winner", "Party A", 1_000, 1, elected=True),
        make_candidate("Independent One", "Independent", 500, 2),
        make_candidate("Independent Two", "Independent", 400, 3),
    ]
    constituency = make_constituency(candidates)

    independents = constituency.get_candidate_by_party("Independent")

    assert [candidate.name for candidate in independents] == [
        "Independent One",
        "Independent Two",
    ]


def test_unknown_candidate_name_raises_key_error():
    constituency = make_constituency(_standard_candidates())

    with pytest.raises(KeyError):
        constituency.get_candidate_by_name("Missing Candidate")


def test_unknown_candidate_party_raises_key_error():
    constituency = make_constituency(_standard_candidates())

    with pytest.raises(KeyError):
        constituency.get_candidate_by_party("Missing Party")


def test_unknown_candidate_place_raises_key_error():
    constituency = make_constituency(_standard_candidates())

    with pytest.raises(KeyError):
        constituency.get_candidate_by_place(99)
