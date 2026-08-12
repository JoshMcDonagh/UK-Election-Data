from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateVotes:
    total: int
    share: float | int
    place: int
