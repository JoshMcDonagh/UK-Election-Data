from datetime import date

from uk_election_data.general.constituencies.candidate_result import ConstituencyCandidateResult


class Constituency:
    def __init__(
            self,
            constituency_id: int,
            election_id: int,
            name: str,
            country: str,
            region: str | None,
            election_date: date,
            total_invalid_votes: int,
            total_registered_voters: int,
            candidate_list: list[ConstituencyCandidateResult]
    ):
        self._constituency_id = constituency_id
        self._election_id = election_id
        self._name = name
        self._country = country
        self._region = region
        self._election_date = election_date
        self._candidate_list = candidate_list.copy()

        self._elected_candidate: str | None = None
        self._winning_party: str | None = None

        self._total_valid_votes: int = 0
        self._total_invalid_votes = total_invalid_votes
        self._total_registered_voters: int = total_registered_voters

        self._candidate_indexes_by_name: dict[str, int] = {}
        self._candidate_indexes_by_party: dict[str, list[int]] = {}
        self._candidate_indexes_by_place: dict[int, int] = {}

        for i in range(len(candidate_list)):
            candidate_result = candidate_list[i]

            if candidate_result.elected:
                if self._elected_candidate is not None or self._winning_party is not None:
                    raise ValueError(f"Expected exactly one elected candidate, but found more than one")

                self._elected_candidate = candidate_result.name
                self._winning_party = candidate_result.party

            self._total_valid_votes += candidate_result.votes.total

            self._candidate_indexes_by_name[candidate_result.name] = i
            if candidate_result.party not in self._candidate_indexes_by_party:
                self._candidate_indexes_by_party[candidate_result.party] = []
            self._candidate_indexes_by_party[candidate_result.party].append(i)
            self._candidate_indexes_by_place[candidate_result.votes.place] = i

        if self._elected_candidate is None or self._winning_party is None:
            raise ValueError(f"Expected exactly one elected candidate, but found none")

    @property
    def constituency_id(self) -> int:
        return self._constituency_id

    @property
    def election_id(self) -> int:
        return self._election_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def country(self) -> str:
        return self._country

    @property
    def region(self) -> str | None:
        return self._region

    @property
    def election_date(self) -> date:
        return self._election_date

    @property
    def candidate_list(self) -> list[ConstituencyCandidateResult]:
        return self._candidate_list.copy()

    @property
    def elected_candidate(self) -> str:
        if self._elected_candidate is None:
            raise ValueError(f"Expected a string but got None")
        return self._elected_candidate

    @property
    def winning_party(self) -> str:
        if self._winning_party is None:
            raise ValueError(f"Expected a string but got None")
        return self._winning_party

    @property
    def total_valid_votes(self) -> int:
        return self._total_valid_votes

    @property
    def total_invalid_votes(self) -> int:
        return self._total_invalid_votes

    @property
    def total_votes(self) -> int:
        return self._total_valid_votes + self._total_invalid_votes

    @property
    def total_registered_voters(self) -> int:
        return self._total_registered_voters

    @property
    def turnout(self) -> float:
        return self.total_votes / self._total_registered_voters

    def get_candidate_by_name(self, name: str) -> ConstituencyCandidateResult:
        return self._candidate_list[self._candidate_indexes_by_name[name]]

    def get_candidate_by_party(self, party: str) -> list[ConstituencyCandidateResult]:
        party_candidate_list: list[ConstituencyCandidateResult] = []

        for index in self._candidate_indexes_by_party[party]:
            party_candidate_list.append(self._candidate_list[index])

        return party_candidate_list

    def get_candidate_by_place(self, place: int) -> ConstituencyCandidateResult:
        return self._candidate_list[self._candidate_indexes_by_place[place]]
