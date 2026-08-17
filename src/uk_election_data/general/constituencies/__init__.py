from collections.abc import Iterator
from typing import Callable, overload

from uk_election_data.general.constituencies.constituency import Constituency


class Constituencies:
    @staticmethod
    def _add_constituency_index(
            index_dict: dict[str, list[int]],
            constituency_identifier: str | None,
            constituency_index: int
    ) -> None:
        if constituency_identifier is None:
            return
        if constituency_identifier in index_dict:
            index_dict[constituency_identifier].append(constituency_index)
        else:
            index_dict[constituency_identifier] = [constituency_index]

    def __init__(self, constituency_list: list[Constituency]):
        self._constituency_list = constituency_list.copy()

        self._constituency_indexes_by_constituency_id: dict[int, int] = {}
        self._constituency_indexes_by_name: dict[str, list[int]] = {}
        self._constituency_indexes_by_country: dict[str, list[int]] = {}
        self._constituency_indexes_by_region: dict[str, list[int]] = {}
        self._constituency_indexes_by_winning_party: dict[str, list[int]] = {}
        self._constituency_indexes_by_elected_candidate: dict[str, list[int]] = {}
        self._constituency_indexes_by_standing_party: dict[str, list[int]] = {}
        self._constituency_indexes_by_candidate_name: dict[str, list[int]] = {}

        for i in range(len(self._constituency_list)):
            constituency = self._constituency_list[i]

            self._constituency_indexes_by_constituency_id[constituency.constituency_id] = i
            Constituencies._add_constituency_index(self._constituency_indexes_by_name, constituency.name, i)
            Constituencies._add_constituency_index(self._constituency_indexes_by_country, constituency.country, i)
            Constituencies._add_constituency_index(self._constituency_indexes_by_region, constituency.region, i)
            Constituencies._add_constituency_index(self._constituency_indexes_by_winning_party, constituency.winning_party, i)
            Constituencies._add_constituency_index(self._constituency_indexes_by_elected_candidate, constituency.elected_candidate, i)

            for candidate_result in constituency.candidate_list:
                Constituencies._add_constituency_index(self._constituency_indexes_by_standing_party, candidate_result.party, i)
                Constituencies._add_constituency_index(self._constituency_indexes_by_candidate_name, candidate_result.name, i)

    def __len__(self) -> int:
        return len(self._constituency_list)

    def __iter__(self) -> Iterator[Constituency]:
        return iter(self._constituency_list)

    @overload
    def __getitem__(self, index: int) -> Constituency: ...

    @overload
    def __getitem__(self, index: slice) -> list[Constituency]: ...

    def __getitem__(self, index: int | slice) -> Constituency | list[Constituency]:
        return self._constituency_list[index]

    @property
    def as_list(self) -> list[Constituency]:
        return self._constituency_list.copy()

    def get_by_id(self, constituency_id: int) -> Constituency:
        return self._constituency_list[self._constituency_indexes_by_constituency_id[constituency_id]]

    def _get_constituencies_by_identifier(
            self,
            index_dict: dict[str, list[int]],
            constituency_identifier: str
    ) -> list[Constituency]:
        if constituency_identifier not in index_dict:
            return []

        constituencies: list[Constituency] = []
        indexes = index_dict[constituency_identifier]
        for index in indexes:
            constituencies.append(self._constituency_list[index])

        return constituencies

    def get_by_name(self, name: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_name, name)

    def get_by_country(self, country: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_country, country)

    def get_by_region(self, region: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_region, region)

    def get_by_winning_party(self, party: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_winning_party, party)

    def get_by_elected_candidate(self, candidate: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_elected_candidate, candidate)

    def get_by_standing_party(self, party: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_standing_party, party)

    def get_by_candidate_name(self, candidate: str) -> list[Constituency]:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_candidate_name, candidate)

    def get_filtered(self, filter_func: Callable[[Constituency], bool]) -> list[Constituency]:
        return [constituency for constituency in self._constituency_list if filter_func(constituency)]
