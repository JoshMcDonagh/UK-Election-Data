from dataclasses import dataclass


@dataclass(frozen=True)
class VotesReceived:
    total: int
    share: float
    place: int


@dataclass(frozen=True)
class Candidate:
    name: str
    party: str
    constituency: str
    election_year: str
    elected: bool
    votes: VotesReceived
