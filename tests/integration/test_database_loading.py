from datetime import date

import pytest

from uk_election_data import (
    all_general_election_dates,
    all_general_election_results,
    general_election_results,
)
from uk_election_data._load_data import load_general_election_result


def test_load_2024_general_election():
    election = load_general_election_result(date(2024, 7, 4))

    assert election.election_id == 6
    assert election.election_date == date(2024, 7, 4)
    assert election.is_notional is False
    assert len(election.constituencies) == 650


def test_2024_database_aggregate_regression_values():
    election = load_general_election_result(date(2024, 7, 4))

    assert election.total_valid_votes == 28_809_340
    assert election.total_invalid_votes == 116_253
    assert election.total_votes == 28_925_593
    assert election.total_registered_voters == 48_224_212
    assert election.turnout == pytest.approx(28_925_593 / 48_224_212)


def test_2024_known_constituency_can_be_looked_up():
    election = load_general_election_result(date(2024, 7, 4))

    [nuneaton] = election.constituencies.get_by_name("Nuneaton")

    assert nuneaton.constituency_id == 1088
    assert nuneaton.winning_party == "Labour"
    assert nuneaton.elected_candidate == "Jodie Gosling"
    assert nuneaton.total_valid_votes == 41_213
    assert nuneaton.total_invalid_votes == 105
    assert nuneaton.total_registered_voters == 71_843


def test_nonexistent_general_election_raises_value_error():
    with pytest.raises(ValueError, match="No general election found for 2000-01-01"):
        load_general_election_result(date(2000, 1, 1))


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known bug: get_general_election_dates currently returns all elections when "
        "include_notional=False and only notional elections when include_notional=True."
    ),
)
def test_general_election_dates_exclude_notional_by_default():
    assert all_general_election_dates() == [
        date(2010, 5, 6),
        date(2015, 5, 7),
        date(2017, 6, 8),
        date(2019, 12, 12),
        date(2024, 7, 4),
    ]


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known bug: include_notional=True currently returns only notionals rather than "
        "the real elections plus notionals."
    ),
)
def test_general_election_dates_include_real_and_notional_when_requested():
    assert all_general_election_dates(include_notional=True) == [
        date(2005, 5, 5),
        date(2010, 5, 6),
        date(2015, 5, 7),
        date(2017, 6, 8),
        date(2019, 12, 12),
        date(2019, 12, 12),
        date(2024, 7, 4),
    ]


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known bug: notional elections have NULL invalid-vote counts, which currently "
        "cause GeneralElection aggregation to add None to int."
    ),
)
def test_2019_notional_general_election_loads():
    election = general_election_results(date(2019, 12, 12), is_notional=True)

    assert election.election_date == date(2019, 12, 12)
    assert election.is_notional is True
    assert len(election.constituencies) == 650


@pytest.mark.xfail(
    strict=True,
    reason="Known date-filtering bug causes the notional-only 2005 date to be loaded as a real election.",
)
def test_all_real_general_election_results_load():
    elections = all_general_election_results()

    assert [election.election_date for election in elections] == [
        date(2010, 5, 6),
        date(2015, 5, 7),
        date(2017, 6, 8),
        date(2019, 12, 12),
        date(2024, 7, 4),
    ]
    assert all(election.is_notional is False for election in elections)
