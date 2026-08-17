from datetime import date

from uk_election_data._load_data import load_general_election_result
from uk_election_data.general.election_result import GeneralElectionResult


def general_election(election_date: date) -> GeneralElectionResult:
    return load_general_election_result(election_date)

