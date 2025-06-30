import csv
from pathlib import Path


def getTeams(file):
    filepath = Path(__file__).parent.parent / "data" / f"{file}"
    teams = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            teams.append(row)
    return teams
