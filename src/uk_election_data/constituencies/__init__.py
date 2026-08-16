from typing import Callable

from uk_election_data.constituencies.candidate_votes import CandidateVotes
from uk_election_data.constituencies.constituency import Constituency


class Constituencies:
    @staticmethod
    def _add_constituency_index(
            index_dict: dict[str, list[int]],
            constituency_identifier: str,
            constituency_index: int
    ) -> None:
        if constituency_identifier in index_dict:
            index_dict[constituency_identifier].append(constituency_index)
        else:
            index_dict[constituency_identifier] = [constituency_index]

    def __init__(self, election_year: str, constituency_list: list[Constituency]):
        self._election_year = election_year
        self._constituency_list = constituency_list

        self._seats_won_by_party: dict[str, int] = {}
        self._votes_by_party: dict[str, int] = {}
        self._total_votes: int = 0
        self._vote_share_by_party: dict[str, float] = {}

        self._constituency_indexes_by_name: dict[str, int] = {}
        self._constituency_indexes_by_region: dict[str, list[int]] = {}
        self._constituency_indexes_by_winning_party: dict[str, list[int]] = {}
        self._constituency_indexes_by_elected_candidate: dict[str, list[int]] = {}
        self._constituency_indexes_by_standing_party: dict[str, list[int]] = {}
        self._constituency_indexes_by_candidate_name: dict[str, list[int]] = {}

        for i in range(len(self._constituency_list)):
            constituency = self._constituency_list[i]

            self._constituency_indexes_by_name[constituency.name] = i
            Constituencies._add_constituency_index(self._constituency_indexes_by_region, constituency.region, i)
            Constituencies._add_constituency_index(self._constituency_indexes_by_winning_party, constituency.winning_party, i)
            Constituencies._add_constituency_index(self._constituency_indexes_by_elected_candidate, constituency.elected_candidate, i)

            for candidate_result in constituency.candidate_results_list:
                if candidate_result.party not in self._seats_won_by_party:
                    self._seats_won_by_party[candidate_result.party] = 0
                    self._votes_by_party[candidate_result.party] = 0

                if candidate_result.elected:
                    self._seats_won_by_party[candidate_result.party] += 1

                self._votes_by_party[candidate_result.party] += candidate_result.vote.total
                self._total_votes += candidate_result.vote.total

                Constituencies._add_constituency_index(self._constituency_indexes_by_standing_party, candidate_result.party, i)
                Constituencies._add_constituency_index(self._constituency_indexes_by_candidate_name, candidate_result.name, i)

        for party, votes in self._votes_by_party.items():
            self._vote_share_by_party[party] = votes / self._total_votes

    @property
    def as_list(self) -> list[Constituency]:
        return self._constituency_list.copy()

    def number_of_seats_won_by_party(self, party: str) -> int:
        return self._seats_won_by_party[party]

    def number_of_votes_by_party(self, party: str) -> int:
        return self._votes_by_party[party]

    @property
    def total_number_of_votes_cast(self) -> int:
        return self._total_votes

    def vote_share_by_party(self, party: str) -> float:
        return self._vote_share_by_party[party]

    def get_at_index(self, index: int) -> Constituency:
        return self._constituency_list[index]

    def get_by_name(self, name: str) -> Constituency:
        return self._constituency_list[self._constituency_indexes_by_name[name]]

    def _get_constituencies_by_identifier(
            self,
            index_dict: dict[str, list[int]],
            constituency_identifier: str
    ) -> list[Constituency] | None:
        if constituency_identifier not in index_dict:
            return None

        constituencies: list[Constituency] = []
        indexes = index_dict[constituency_identifier]
        for index in indexes:
            constituencies.append(self._constituency_list[index])

        return constituencies

    def get_by_region(self, region: str) -> list[Constituency] | None:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_region, region)

    def get_by_winning_party(self, party: str) -> list[Constituency] | None:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_winning_party, party)

    def get_by_elected_candidate(self, candidate: str) -> list[Constituency] | None:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_elected_candidate, candidate)

    def get_by_standing_party(self, party: str) -> list[Constituency] | None:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_standing_party, party)

    def get_by_candidate_name(self, candidate: str) -> list[Constituency] | None:
        return self._get_constituencies_by_identifier(self._constituency_indexes_by_candidate_name, candidate)

    def get_filtered(self, filter_func: Callable[[Constituency], bool]) -> list[Constituency]:
        return [constituency for constituency in self._constituency_list if filter_func(constituency)]
