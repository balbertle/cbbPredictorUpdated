from helpers.getTeams import getTeams
import numpy as np

def best_pythagorean_exponent(file):
    teams = getTeams(file)
    exponents = np.arange(0.001, 20.001, 0.001)

    best_exponent = None
    smallest_total_error = float('inf')

    for exp in exponents:
        total_error = 0
        valid_team_count = 0

        for team in teams:
            try:
                adj_oe = float(team["ADJOE"])
                adj_de = float(team["ADJDE"])
                adj_tempo = float(team["ADJ_T"])
                wins = float(team["W"])
                games = float(team["G"])

                pts_for = adj_oe * 100 / adj_tempo
                pts_against = adj_de * 100 / adj_tempo

                expected_win_pct = pts_for**exp / (pts_for**exp + pts_against**exp)
                actual_win_pct = wins / games


                error = abs(expected_win_pct - actual_win_pct)
                total_error += error
                valid_team_count += 1

            except (KeyError, ValueError, ZeroDivisionError):
                continue  # Skip teams with missing or invalid data

        if valid_team_count == 0:
            continue

        avg_error = total_error / valid_team_count

        if avg_error < smallest_total_error:
            smallest_total_error = avg_error
            best_exponent = exp

    print(f"Best exponent for {file}: {best_exponent:.3f} with average error: {smallest_total_error:.5f}")
    return best_exponent

# Run it
best_pythagorean_exponent("cbb25.csv") # best for 2025 is 4.386 with average error of 0.09415
