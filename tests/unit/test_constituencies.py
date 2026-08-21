import pytest

from tests.factories import make_candidate, make_constituency
from uk_election_data.general.constituencies import Constituencies


def _collection():
    alpha = make_constituency(
        [
            make_candidate("Alice Alpha", "Labour", 1_000, 1, elected=True),
            make_candidate("Bob Alpha", "Conservative", 800, 2),
            make_candidate("Ian Alpha", "Independent", 100, 3),
        ],
        constituency_id=1,
        election_id=101,
        name="Alpha",
        country="England",
        region="North West",
    )

    beta = make_constituency(
        [
            make_candidate("Carol Beta", "Conservative", 1_100, 1, elected=True),
            make_candidate("Dan Beta", "Labour", 900, 2),
        ],
        constituency_id=2,
        election_id=102,
        name="Beta",
        country="England",
        region="London",
    )

    gamma = make_constituency(
        [
            make_candidate("Eve Gamma", "SNP", 1_200, 1, elected=True),
            make_candidate("Ian Gamma One", "Independent", 300, 2),
            make_candidate("Ian Gamma Two", "Independent", 200, 3),
        ],
        constituency_id=3,
        election_id=103,
        name="Gamma",
        country="Scotland",
        region=None,
    )

    return Constituencies([alpha, beta, gamma]), alpha, beta, gamma


def test_len_iteration_and_integer_indexing():
    constituencies, alpha, beta, gamma = _collection()

    assert len(constituencies) == 3
    assert list(constituencies) == [alpha, beta, gamma]
    assert constituencies[0] is alpha
    assert constituencies[-1] is gamma


def test_slice_indexing_returns_list():
    constituencies, alpha, beta, _ = _collection()

    assert constituencies[:2] == [alpha, beta]
    assert isinstance(constituencies[:2], list)


def test_constructor_copies_input_list():
    constituencies, alpha, beta, gamma = _collection()
    original = [alpha, beta, gamma]
    copied_collection = Constituencies(original)

    original.clear()

    assert copied_collection.as_list == [alpha, beta, gamma]


def test_as_list_returns_defensive_copy():
    constituencies, alpha, beta, gamma = _collection()

    result = constituencies.as_list
    result.clear()

    assert constituencies.as_list == [alpha, beta, gamma]


def test_get_by_id():
    constituencies, _, beta, _ = _collection()

    assert constituencies.get_by_id(2) is beta


def test_get_by_name():
    constituencies, alpha, _, _ = _collection()

    assert constituencies.get_by_name("Alpha") == [alpha]


def test_get_by_country():
    constituencies, alpha, beta, _ = _collection()

    assert constituencies.get_by_country("England") == [alpha, beta]


def test_get_by_region():
    constituencies, _, beta, _ = _collection()

    assert constituencies.get_by_region("London") == [beta]


def test_none_region_is_not_indexed():
    constituencies, _, _, _ = _collection()

    assert constituencies.get_by_region("None") == []


def test_get_by_winning_party():
    constituencies, alpha, _, _ = _collection()

    assert constituencies.get_by_winning_party("Labour") == [alpha]


def test_get_by_elected_candidate():
    constituencies, _, _, gamma = _collection()

    assert constituencies.get_by_elected_candidate("Eve Gamma") == [gamma]


def test_get_by_standing_party():
    constituencies, alpha, beta, _ = _collection()

    assert constituencies.get_by_standing_party("Labour") == [alpha, beta]


def test_get_by_candidate_name():
    constituencies, _, beta, _ = _collection()

    assert constituencies.get_by_candidate_name("Dan Beta") == [beta]


def test_unknown_string_identifier_returns_empty_list():
    constituencies, _, _, _ = _collection()

    assert constituencies.get_by_name("Missing") == []
    assert constituencies.get_by_country("Missing") == []
    assert constituencies.get_by_region("Missing") == []
    assert constituencies.get_by_winning_party("Missing") == []
    assert constituencies.get_by_elected_candidate("Missing") == []
    assert constituencies.get_by_standing_party("Missing") == []
    assert constituencies.get_by_candidate_name("Missing") == []


def test_unknown_constituency_id_raises_key_error():
    constituencies, _, _, _ = _collection()

    with pytest.raises(KeyError):
        constituencies.get_by_id(999)


def test_get_filtered():
    constituencies, alpha, beta, _ = _collection()

    result = constituencies.get_filtered(lambda constituency: constituency.country == "England")

    assert result == [alpha, beta]


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Known bug: a constituency is indexed once per matching candidate, so a party "
        "such as Independent can return the same constituency more than once."
    ),
)
def test_get_by_standing_party_does_not_duplicate_constituency():
    constituencies, alpha, _, gamma = _collection()

    assert constituencies.get_by_standing_party("Independent") == [alpha, gamma]
