from datetime import date

import pytest

import uk_election_data


def test_all_general_election_dates_delegates_to_loader(monkeypatch):
    expected = [date(2019, 12, 12), date(2024, 7, 4)]
    calls = []

    def fake_get_dates(include_notional=False):
        calls.append(include_notional)
        return expected

    monkeypatch.setattr(uk_election_data, "get_general_election_dates", fake_get_dates)

    assert uk_election_data.all_general_election_dates(True) is expected
    assert calls == [True]


@pytest.mark.xfail(
    strict=True,
    reason="Known bug: general_election_results checks the cache but never stores newly loaded elections in it.",
)
def test_general_election_results_caches_loaded_result(monkeypatch):
    sentinel = object()
    calls = []

    def fake_load(election_date, is_notional=False):
        calls.append((election_date, is_notional))
        return sentinel

    monkeypatch.setattr(uk_election_data, "load_general_election_result", fake_load)
    election_date = date(2024, 7, 4)

    first = uk_election_data.general_election_results(election_date)
    second = uk_election_data.general_election_results(election_date)

    assert first is sentinel
    assert second is sentinel
    assert calls == [(election_date, False)]


@pytest.mark.xfail(
    strict=True,
    reason="Known bug: normal and notional election results are not inserted into their separate caches.",
)
def test_normal_and_notional_results_use_separate_caches(monkeypatch):
    normal = object()
    notional = object()
    calls = []

    def fake_load(election_date, is_notional=False):
        calls.append((election_date, is_notional))
        return notional if is_notional else normal

    monkeypatch.setattr(uk_election_data, "load_general_election_result", fake_load)
    election_date = date(2019, 12, 12)

    assert uk_election_data.general_election_results(election_date, False) is normal
    assert uk_election_data.general_election_results(election_date, True) is notional
    assert uk_election_data.general_election_results(election_date, False) is normal
    assert uk_election_data.general_election_results(election_date, True) is notional
    assert calls == [
        (election_date, False),
        (election_date, True),
    ]


def test_all_general_election_results_maps_second_duplicate_date_to_notional(monkeypatch):
    election_2019 = date(2019, 12, 12)
    election_2024 = date(2024, 7, 4)
    calls = []

    monkeypatch.setattr(
        uk_election_data,
        "all_general_election_dates",
        lambda include_notional=False: [election_2019, election_2019, election_2024],
    )

    def fake_results(election_date, is_notional=False):
        calls.append((election_date, is_notional))
        return (election_date, is_notional)

    monkeypatch.setattr(uk_election_data, "general_election_results", fake_results)

    result = uk_election_data.all_general_election_results(include_notional=True)

    assert result == [
        (election_2019, False),
        (election_2019, True),
        (election_2024, False),
    ]
    assert calls == result


def test_all_general_election_results_skips_duplicate_date_when_not_including_notional(monkeypatch):
    election_2019 = date(2019, 12, 12)
    calls = []

    monkeypatch.setattr(
        uk_election_data,
        "all_general_election_dates",
        lambda include_notional=False: [election_2019, election_2019],
    )

    def fake_results(election_date, is_notional=False):
        calls.append((election_date, is_notional))
        return (election_date, is_notional)

    monkeypatch.setattr(uk_election_data, "general_election_results", fake_results)

    result = uk_election_data.all_general_election_results(include_notional=False)

    assert result == [(election_2019, False)]
    assert calls == [(election_2019, False)]


def test_all_general_election_results_caches_complete_result_list(monkeypatch):
    calls = 0

    def fake_dates(include_notional=False):
        nonlocal calls
        calls += 1
        return [date(2024, 7, 4)]

    monkeypatch.setattr(uk_election_data, "all_general_election_dates", fake_dates)
    monkeypatch.setattr(
        uk_election_data,
        "general_election_results",
        lambda election_date, is_notional=False: object(),
    )

    first = uk_election_data.all_general_election_results()
    second = uk_election_data.all_general_election_results()

    assert first is second
    assert calls == 1


@pytest.mark.xfail(
    strict=True,
    reason="Known API-safety issue: the cached list is returned directly and can be mutated by callers.",
)
def test_all_general_election_results_returns_defensive_copy(monkeypatch):
    monkeypatch.setattr(
        uk_election_data,
        "all_general_election_dates",
        lambda include_notional=False: [date(2024, 7, 4)],
    )
    monkeypatch.setattr(
        uk_election_data,
        "general_election_results",
        lambda election_date, is_notional=False: object(),
    )

    first = uk_election_data.all_general_election_results()
    first.clear()
    second = uk_election_data.all_general_election_results()

    assert len(second) == 1
