from helpers.getTeams import getTeams
from helpers.findTeam import findTeam

def pythagoreanExpectation(teamName, exponent, file):
    """Calculate Pythagorean expectation using points for and against"""
    team = findTeam(teamName, file)
    ptsFor = float(team["ADJOE"]) * 100 / float(team["ADJ_T"])
    ptsAgainst = float(team["ADJDE"]) * 100 / float(team['ADJ_T'])

    if ptsFor is None or ptsAgainst is None:
        print(f"Warning: Team '{teamName}' not found in the data. Using default probability of 0.5")
        return 0.5
    
    percentage = ptsFor**(exponent) / (ptsFor**4.(exponent) + ptsAgainst**(exponent))
    print("Real win rate: ")
    print(float(team["W"]) / float(team["G"]))
    return percentage


def print_actual_vs_expected(file, exponent):
    teams = getTeams(file)

    print(f"{'Team':<25} {'Actual Win%':<15} {'Expected Win%':<15}")
    print("-" * 55)

    for team in teams:
        try:
            adj_oe = float(team["ADJOE"])
            adj_de = float(team["ADJDE"])
            adj_tempo = float(team["ADJ_T"])
            wins = float(team["W"])
            games = float(team["G"])

            pts_for = adj_oe * 100 / adj_tempo
            pts_against = adj_de * 100 / adj_tempo

            expected_win_pct = pts_for**exponent / (pts_for**exponent + pts_against**exponent)
            actual_win_pct = wins / games

            print(f"{team['Team']:<25} {actual_win_pct:<15.3f} {expected_win_pct:<15.3f}")

        except (KeyError, ValueError, ZeroDivisionError):
            continue  # Skip any invalid team entries
