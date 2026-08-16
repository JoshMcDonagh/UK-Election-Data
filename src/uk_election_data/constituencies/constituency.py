from uk_election_data.constituencies.candidate import Candidate


class Constituency:
    def __init__(
            self,
            name: str,
            region: str,
            election_year: int,
            candidate_results: list[Candidate]
    ):
        self._name = name
        self._region = region
        self._election_year = election_year
        self._candidate_results_list = candidate_results

        self._elected_candidate: str
        self._winning_party: str

        self._total_votes: int = 0

        self._candidate_indexes_by_name: dict[str, int] = {}
        self._candidate_indexes_by_party: dict[str, int] = {}
        self._candidate_indexes_by_place: dict[int, int] = {}

        for i in range(len(candidate_results)):
            candidate_result = candidate_results[i]

            if candidate_result.elected:
                self._elected_candidate = candidate_result.name
                self._winning_party = candidate_result.party

            self._total_votes += candidate_result.votes.total

            self._candidate_indexes_by_name[candidate_result.name] = i
            self._candidate_indexes_by_party[candidate_result.party] = i
            self._candidate_indexes_by_place[candidate_result.votes.place] = i

    @property
    def name(self) -> str:
        return self._name

    @property
    def region(self) -> str:
        return self._region

    @property
    def election_year(self) -> int:
        return self._election_year

    @property
    def candidate_results_list(self) -> list[Candidate]:
        return self._candidate_results_list.copy()

    @property
    def elected_candidate(self) -> str:
        return self._elected_candidate

    @property
    def winning_party(self) -> str:
        return self._winning_party

    @property
    def total_number_of_votes_cast(self) -> int:
        return self._total_votes

    def get_candidate_by_name(self, name: str) -> Candidate:
        return self._candidate_results_list[self._candidate_indexes_by_name[name]]

    def get_candidate_by_party(self, party: str) -> Candidate:
        return self._candidate_results_list[self._candidate_indexes_by_party[party]]

    def get_candidate_by_place(self, place: int) -> Candidate:
        return self._candidate_results_list[self._candidate_indexes_by_place[place]]
