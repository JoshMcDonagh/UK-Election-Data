from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class VotesReceived:
    total: int
    share: float
    place: int


@dataclass(frozen=True)
class CandidateResult:
    candidacy_id: int
    constituency_id: int
    election_id: int
    name: str
    party: str
    constituency: str
    election_date: date
    elected: bool
    votes: VotesReceived
