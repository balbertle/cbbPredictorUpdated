import numpy as np

from scipy.stats import norm


from helpers.getTeams import getTeams
from helpers.findTeam import findTeam 
from helperFunctions import data
from helpers.prepare_stats import prepare_team_stats, calculate_league_averages
from mathHelpers.log5 import calculate_four_factors_probabilities


points_per_state = {
    'Start': 0, 'Make 2': 2, 'Make 3': 3, 'Missed Shot': 0, 'Turnover': 0, 'Offensive Rebound': 0,
    'Shooting Foul 2-Shots': 0, 'Shooting Foul 3-Shots': 0, 'FT 1-of-2': 0, 'FT 2-of-2': 1,
    'FT 1-of-3': 0, 'FT 2-of-3': 1, 'FT 3-of-3': 1, 'Make 2 + Foul (And-One)': 2, 'And-One FT': 1, 'End': 0
}
def create_transition_matrix(probs):
    states = list(points_per_state.keys()); matrix = np.zeros((len(states), len(states))); state_idx = {state: i for i, state in enumerate(states)}
    p_make_2, p_make_3, p_ft_make, p_orb = probs['p_make_2'], probs['p_make_3'], probs['p_ft_make'], probs['p_offensive_rebound']
    start_idx = state_idx['Start']
    matrix[start_idx, state_idx['Make 2']] = probs['p_fga_2'] * p_make_2; matrix[start_idx, state_idx['Missed Shot']] = probs['p_fga_2'] * (1 - p_make_2)
    matrix[start_idx, state_idx['Make 3']] = probs['p_fga_3'] * p_make_3; matrix[start_idx, state_idx['Missed Shot']] += probs['p_fga_3'] * (1 - p_make_3)
    matrix[start_idx, state_idx['Turnover']] = probs['p_turnover']; matrix[start_idx, state_idx['Shooting Foul 2-Shots']] = probs['p_foul_on_2']
    matrix[start_idx, state_idx['Shooting Foul 3-Shots']] = probs['p_foul_on_3']; matrix[start_idx, state_idx['Make 2 + Foul (And-One)']] = probs['p_and_one']
    matrix[state_idx['Make 2'], state_idx['End']] = 1; matrix[state_idx['Make 3'], state_idx['End']] = 1; matrix[state_idx['Turnover'], state_idx['End']] = 1
    matrix[state_idx['Missed Shot'], state_idx['Offensive Rebound']] = p_orb; matrix[state_idx['Missed Shot'], state_idx['End']] = 1 - p_orb
    matrix[state_idx['Offensive Rebound'], state_idx['Start']] = 1; matrix[state_idx['Shooting Foul 2-Shots'], state_idx['FT 1-of-2']] = 1
    matrix[state_idx['Shooting Foul 3-Shots'], state_idx['FT 1-of-3']] = 1; matrix[state_idx['FT 1-of-2'], state_idx['FT 2-of-2']] = 1
    matrix[state_idx['FT 2-of-2'], state_idx['Offensive Rebound']] = (1 - p_ft_make) * p_orb; matrix[state_idx['FT 2-of-2'], state_idx['End']] = 1 - ((1 - p_ft_make) * p_orb)
    matrix[state_idx['FT 1-of-3'], state_idx['FT 2-of-3']] = 1; matrix[state_idx['FT 2-of-3'], state_idx['FT 3-of-3']] = 1
    matrix[state_idx['FT 3-of-3'], state_idx['Offensive Rebound']] = (1 - p_ft_make) * p_orb; matrix[state_idx['FT 3-of-3'], state_idx['End']] = 1 - ((1 - p_ft_make) * p_orb)
    matrix[state_idx['Make 2 + Foul (And-One)'], state_idx['And-One FT']] = 1; matrix[state_idx['And-One FT'], state_idx['Offensive Rebound']] = (1 - p_ft_make) * p_orb
    matrix[state_idx['And-One FT'], state_idx['End']] = 1 - ((1 - p_ft_make) * p_orb); matrix[state_idx['End'], state_idx['End']] = 1
    row_sums = matrix.sum(axis=1); row_sums[row_sums == 0] = 1; matrix = matrix / row_sums[:, np.newaxis]
    return matrix
def simulate_game(team1_matrix, team2_matrix, num_possessions, max_steps_per_possession=15):
    states = list(points_per_state.keys()); state_index = {state: i for i, state in enumerate(states)}; team_points = {1: 0, 2: 0}
    total_state_counts = {state: 0 for state in states}; current_team_idx = 1
    for _ in range(int(num_possessions * 2)):
        transition_matrix = team1_matrix if current_team_idx == 1 else team2_matrix
        current_state = 'Start'; steps = 0
        while current_state != 'End' and steps < max_steps_per_possession:
            team_points[current_team_idx] += points_per_state.get(current_state, 0); total_state_counts[current_state] += 1
            row = transition_matrix[state_index[current_state]]; current_state = np.random.choice(states, p=row); steps += 1
        total_state_counts['End'] += 1; team_points[current_team_idx] += points_per_state.get(current_state, 0); current_team_idx = 3 - current_team_idx
    return team_points[1], team_points[2], total_state_counts

import numpy as np

def get_barthag_win_prob(barthag1, barthag2):
    """
    Calculates the win probability between two teams based on their BARTHAG ratings
    using the Log5 formula.
    """
    # The Log5 formula: P(A wins) = (A - A*B) / (A + B - 2*A*B)
    denominator = barthag1 + barthag2 - 2 * barthag1 * barthag2
    if denominator == 0:
        return 0.5
    return (barthag1 - barthag1 * barthag2) / denominator


def simulate_matchup(
    team1_name, team1_stats, 
    team2_name, team2_stats, 
    league_averages, 
    exponent, 
    pythag_weight=0.10,
    barthag_weight=0,
    num_simulations=500
):
    print(f"\nSimulating matchup: {team1_name} vs {team2_name}")
    possessions = (team1_stats["poss_per_g"] + team2_stats["poss_per_g"]) / 2
    
    team1_probs = calculate_four_factors_probabilities(team1_stats, team2_stats, league_averages)
    team2_probs = calculate_four_factors_probabilities(team2_stats, team1_stats, league_averages)
    
    team1_matrix = create_transition_matrix(team1_probs)
    team2_matrix = create_transition_matrix(team2_probs)
    
    team1_scores = []
    team2_scores = []
    score_diffs = []

    print(f"Running {num_simulations} simulations...")
    for i in range(num_simulations):
        if (i + 1) % 100 == 0 or i == num_simulations - 1:
            print(f"\r  Simulation {i + 1}/{num_simulations}", end="")
            
        score1, score2, _ = simulate_game(team1_matrix, team2_matrix, possessions)
        
        team1_scores.append(score1)
        team2_scores.append(score2)
        score_diffs.append(score1 - score2)
    
    print(f"\r  Simulation Complete.                         ")

    # --- Calculate All Probabilities ---
    
    # 1. Probability from the detailed simulation
    p_win_log5 = sum(1 for diff in score_diffs if diff > 0) / num_simulations
    
    # 2. Probability from Pythagorean Expectation
    p_win_pythag = get_pythagorean_win_prob(team1_stats, team2_stats, exponent, league_averages)
    
    # 3. Probability from BARTHAG rating
    p_win_barthag = get_barthag_win_prob(team1_stats['BARTHAG'], team2_stats['BARTHAG'])
    
    # --- Blend the results ---
    log5_weight = 1.0 - pythag_weight - barthag_weight
    final_win_prob = (
        (p_win_log5 * log5_weight) + 
        (p_win_pythag * pythag_weight) + 
        (p_win_barthag * barthag_weight)
    )

    # --- Calculate Final Averages ---
    team1_avg = np.mean(team1_scores)
    team2_avg = np.mean(team2_scores)
    spread_mean = np.mean(score_diffs)
    
    # --- Print Corrected and Consistent Results ---
    print("\n--- Model Predictions ---")
    print(f"Predicted Final Score: {team1_name} {team1_avg:.1f} - {team2_name} {team2_avg:.1f}")
    print(f"{team1_name} Win Probability: {final_win_prob:.2%}")

    print("\n--- Betting Market Analysis ---")
    print(f"Predicted Spread: {team1_name} {spread_mean:-.1f}")
    print(f"Predicted Total (Over/Under): {team1_avg + team2_avg:.1f}")
    

    # 3. Calculate the average score differential (the spread).
    spread_mean = np.mean(score_diffs)
    

    # Determine the winner based on our robust win probability calculation.
    winner_name = team1_name if final_win_prob > 0.5 else team2_name
    return winner_name
def get_pythagorean_win_prob(team1_stats, team2_stats, exponent, league_averages):
    """
    Calculates the win probability for team1 against team2 using Pythagorean Expectation and backtested exponent.
    """
    league_avg_ppp = league_averages['PPG']

    team1_expected_score = (team1_stats['ADJOE'] * team2_stats['ADJDE']) / league_avg_ppp
    team2_expected_score = (team2_stats['ADJOE'] * team1_stats['ADJDE']) / league_avg_ppp

    # Apply the Pythagorean formula
    win_prob_team1 = team1_expected_score**exponent / (team1_expected_score**exponent + team2_expected_score**exponent)

    return win_prob_team1

def main():
    """Main execution function demonstrating the new, more accurate workflow."""


    all_teams_csv = getTeams("cbb25.csv")
    if not all_teams_csv: return

    league_averages = calculate_league_averages(all_teams_csv, data)

    team1_name = "wofford"
    team2_name = "tennessee"

    team1_csv = findTeam(team1_name, "cbb25.csv")
    team1_obj = data(team1_name)
    team2_csv = findTeam(team2_name, "cbb25.csv")
    team2_obj = data(team2_name)

    if not all((team1_csv, team1_obj, team2_csv, team2_obj)):
        print("\nCould not find all required data for one or both teams. Exiting.")
        return

    team1_stats = prepare_team_stats(team1_csv, team1_obj)
    print(team1_stats)
    team2_stats = prepare_team_stats(team2_csv, team2_obj)
    print(team2_stats)
    if not team1_stats or not team2_stats:
        print("\nCould not prepare advanced stats for one or both teams. Exiting.")
        return

    simulate_matchup(team1_name, team1_stats,
                     team2_name, team2_stats,
                     league_averages,4.386,pythag_weight=0.10, barthag_weight=0.1, num_simulations=200)

if __name__ == "__main__":
    main()