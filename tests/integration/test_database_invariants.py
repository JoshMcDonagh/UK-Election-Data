from datetime import date

import pytest

from uk_election_data._load_data import load_general_election_result


def test_2024_every_constituency_has_exactly_one_elected_candidate():
    election = load_general_election_result(date(2024, 7, 4))

    for constituency in election.constituencies:
        elected = [candidate for candidate in constituency.candidate_list if candidate.elected]
        assert len(elected) == 1, constituency.name
        assert elected[0].name == constituency.elected_candidate
        assert elected[0].party == constituency.winning_party


def test_2024_constituency_vote_totals_equal_candidate_vote_sums():
    election = load_general_election_result(date(2024, 7, 4))

    for constituency in election.constituencies:
        assert constituency.total_valid_votes == sum(
            candidate.votes.total for candidate in constituency.candidate_list
        ), constituency.name


def test_2024_candidate_places_are_unique_within_each_constituency():
    election = load_general_election_result(date(2024, 7, 4))

    for constituency in election.constituencies:
        places = [candidate.votes.place for candidate in constituency.candidate_list]
        assert len(places) == len(set(places)), constituency.name


def test_2024_turnout_is_between_zero_and_one():
    election = load_general_election_result(date(2024, 7, 4))

    assert 0 < election.turnout < 1
    for constituency in election.constituencies:
        assert 0 < constituency.turnout < 1, constituency.name


def test_2024_party_vote_totals_sum_to_total_valid_votes():
    election = load_general_election_result(date(2024, 7, 4))
    parties = {candidate.party for constituency in election.constituencies for candidate in constituency.candidate_list}

    assert sum(election.number_of_votes_by_party(party) for party in parties) == election.total_valid_votes
    assert sum(election.vote_share_by_party(party) for party in parties) == pytest.approx(1.0)


def test_2024_party_seat_totals_sum_to_650():
    election = load_general_election_result(date(2024, 7, 4))
    parties = {candidate.party for constituency in election.constituencies for candidate in constituency.candidate_list}

    assert sum(election.number_of_seats_won_by_party(party) for party in parties) == 650


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known bug: get_by_standing_party indexes a constituency once per candidate, "
        "so constituencies with multiple Independent candidates are duplicated."
    ),
)
def test_2024_standing_party_results_contain_unique_constituencies():
    election = load_general_election_result(date(2024, 7, 4))

    independents = election.constituencies.get_by_standing_party("Independent")

    ids = [constituency.constituency_id for constituency in independents]
    assert len(ids) == len(set(ids))
