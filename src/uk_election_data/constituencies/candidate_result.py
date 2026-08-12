from dataclasses import dataclass

from uk_election_data.constituencies.candidate_votes import CandidateVotes


@dataclass(frozen=True)
class CandidateResult:
    name: str
    party: str
    constituency: str
    election_year: str
    elected: bool
    vote: CandidateVotes
