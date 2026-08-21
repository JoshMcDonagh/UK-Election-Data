from datetime import date

import pytest

from tests.factories import make_candidate, make_constituency
from uk_election_data.general.constituencies import Constituencies
from uk_election_data.general.election_result import GeneralElection


def _election():
    alpha = make_constituency(
        [
            make_candidate("Alice", "Labour", 1_000, 1, elected=True),
            make_candidate("Bob", "Conservative", 800, 2),
            make_candidate("Indie", "Independent", 200, 3),
        ],
        constituency_id=1,
        election_id=101,
        name="Alpha",
        invalid_votes=20,
        registered_voters=3_000,
    )
    beta = make_constituency(
        [
            make_candidate("Carol", "Conservative", 1_100, 1, elected=True),
            make_candidate("Dan", "Labour", 900, 2),
        ],
        constituency_id=2,
        election_id=102,
        name="Beta",
        invalid_votes=30,
        registered_voters=3_500,
    )

    return GeneralElection(
        election_id=7,
        election_date=date(2024, 7, 4),
        is_notional=False,
        constituencies=Constituencies([alpha, beta]),
    )


def test_general_election_stores_metadata():
    election = _election()

    assert election.election_id == 7
    assert election.election_date == date(2024, 7, 4)
    assert election.is_notional is False
    assert len(election.constituencies) == 2


def test_general_election_aggregates_vote_and_electorate_totals():
    election = _election()

    assert election.total_valid_votes == 4_000
    assert election.total_invalid_votes == 50
    assert election.total_votes == 4_050
    assert election.total_registered_voters == 6_500
    assert election.turnout == pytest.approx(4_050 / 6_500)


def test_number_of_seats_won_by_party():
    election = _election()

    assert election.number_of_seats_won_by_party("Labour") == 1
    assert election.number_of_seats_won_by_party("Conservative") == 1
    assert election.number_of_seats_won_by_party("Independent") == 0


def test_number_of_votes_by_party():
    election = _election()

    assert election.number_of_votes_by_party("Labour") == 1_900
    assert election.number_of_votes_by_party("Conservative") == 1_900
    assert election.number_of_votes_by_party("Independent") == 200


def test_vote_share_by_party():
    election = _election()

    assert election.vote_share_by_party("Labour") == pytest.approx(1_900 / 4_000)
    assert election.vote_share_by_party("Conservative") == pytest.approx(1_900 / 4_000)
    assert election.vote_share_by_party("Independent") == pytest.approx(200 / 4_000)


def test_party_vote_shares_sum_to_one():
    election = _election()
    parties = ["Labour", "Conservative", "Independent"]

    total = sum(election.vote_share_by_party(party) for party in parties)

    assert total == pytest.approx(1.0)


def test_party_seat_counts_sum_to_number_of_constituencies():
    election = _election()
    parties = ["Labour", "Conservative", "Independent"]

    total = sum(election.number_of_seats_won_by_party(party) for party in parties)

    assert total == len(election.constituencies)


def test_unknown_party_raises_key_error():
    election = _election()

    with pytest.raises(KeyError):
        election.number_of_votes_by_party("Missing Party")
    with pytest.raises(KeyError):
        election.number_of_seats_won_by_party("Missing Party")
    with pytest.raises(KeyError):
        election.vote_share_by_party("Missing Party")
