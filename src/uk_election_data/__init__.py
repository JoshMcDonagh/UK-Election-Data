from datetime import date

from uk_election_data._load_data import load_general_election_result, get_general_election_dates
from uk_election_data.general.election_result import GeneralElection

_ge_cache: dict[date, GeneralElection] = {}

_notional_ge_cache: dict[date, GeneralElection] = {}

_all_ge_cache: list[GeneralElection] | None = None

_all_ge_with_notional_cache: list[GeneralElection] | None = None


def all_general_election_dates(include_notional: bool = False) -> list[date]:
    return get_general_election_dates(include_notional)


def general_election_results(election_date: date, is_notional: bool = False) -> GeneralElection:
    if is_notional and election_date in _notional_ge_cache:
        return _notional_ge_cache[election_date]

    if not is_notional and election_date in _ge_cache:
        return _ge_cache[election_date]

    return load_general_election_result(election_date, is_notional)


def all_general_election_results(include_notional: bool = False) -> list[GeneralElection]:
    global _all_ge_with_notional_cache
    global _all_ge_cache

    if include_notional and _all_ge_with_notional_cache is not None:
        return _all_ge_with_notional_cache

    if not include_notional and _all_ge_cache is not None:
        return _all_ge_cache

    ge_results: list[GeneralElection] = []

    ge_date_counts: dict[date, int] = {}
    ge_dates = all_general_election_dates(include_notional)

    for ge_date in ge_dates:
        ge_date_counts[ge_date] = 0

    for ge_date in ge_dates:
        ge_date_counts[ge_date] += 1

        if ge_date_counts[ge_date] >= 3 or (ge_date_counts[ge_date] >= 2 and not include_notional):
            continue

        if ge_date_counts[ge_date] == 2 and include_notional:
            is_notional = True
        else:
            is_notional = False

        ge_results.append(general_election_results(ge_date, is_notional))

    if include_notional:
        _all_ge_with_notional_cache = ge_results
    else:
        _all_ge_cache = ge_results

    return ge_results
