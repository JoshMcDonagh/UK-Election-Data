from datetime import date

from uk_election_data.general.constituencies import Constituencies


class GeneralElectionResult:
    def __init__(self, election_id: int, election_date: date, constituencies: Constituencies):
        self._election_id = election_id
        self._election_date = election_date
        self._constituencies = constituencies

        self._seats_won_by_party: dict[str, int] = {}
        self._votes_by_party: dict[str, int] = {}
        self._total_valid_votes: int = 0
        self._total_invalid_votes: int = 0
        self._total_registered_voters: int = 0
        self._vote_share_by_party: dict[str, float] = {}

        for constituency in constituencies:
            self._total_invalid_votes += constituency.total_invalid_votes
            self._total_registered_voters += constituency.total_registered_voters

            for candidate_result in constituency.candidate_list:
                if candidate_result.party not in self._seats_won_by_party:
                    self._seats_won_by_party[candidate_result.party] = 0
                    self._votes_by_party[candidate_result.party] = 0

                if candidate_result.elected:
                    self._seats_won_by_party[candidate_result.party] += 1

                self._votes_by_party[candidate_result.party] += candidate_result.votes.total
                self._total_valid_votes += candidate_result.votes.total

        for party, votes in self._votes_by_party.items():
            self._vote_share_by_party[party] = votes / self._total_valid_votes

    @property
    def election_id(self) -> int:
        return self._election_id

    @property
    def election_date(self) -> date:
        return self._election_date

    @property
    def constituencies(self) -> Constituencies:
        return self._constituencies

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
        return self.total_votes / self.total_registered_voters

    def number_of_seats_won_by_party(self, party: str) -> int:
        return self._seats_won_by_party[party]

    def number_of_votes_by_party(self, party: str) -> int:
        return self._votes_by_party[party]

    def vote_share_by_party(self, party: str) -> float:
        return self._vote_share_by_party[party]
