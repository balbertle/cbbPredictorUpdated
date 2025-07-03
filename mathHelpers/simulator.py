import numpy as np
from scipy.stats import norm
from helpers.getTeams import getTeams
from helpers.findTeam import findTeam
from mathHelpers.bayesian import probabilities
from mathHelpers.unweighted import probabilitiesUnweighted

points_per_state = {
    'Start': 0,
    'Make 2': 2,
    'Make 3': 3,
    'Failed Possession': 0,
    'Free Throw 1': 1,
    'Free Throw 2': 1,
    'And-One': 1,
    'Offensive Rebound': 0,
    'End': 0
}


import numpy as np

def simulate_game(team1_matrix, team2_matrix, points_per_state, num_possessions, show_progress=False):
    import numpy as np

    states = list(points_per_state.keys())
    state_index = {state: i for i, state in enumerate(states)}
    state_counts = {state: 0 for state in states}
    team_points = {1: 0, 2: 0}

    current_team = 1
    possession_count = 0

    while possession_count < num_possessions:
        if show_progress:
            print(f"\rPossession {possession_count + 1}/{num_possessions}", end="")

        transition_matrix = team1_matrix if current_team == 1 else team2_matrix
        current_state = 'Start'
        possession_count += 0.5
        steps = 0

        while current_state != 'End' and steps < 10:
            row = transition_matrix[state_index[current_state]]
            row = np.maximum(row, 0)
            total = row.sum()
            next_state = 'End' if total == 0 else np.random.choice(states, p=row / total)

            team_points[current_team] += points_per_state.get(next_state, 0)
            state_counts[next_state] += 1

            current_state = next_state
            steps += 1

        # Force End count if needed
        if current_state != 'End':
            state_counts['End'] += 1

        current_team = 3 - current_team  # Switch teams


    if show_progress:
        print()

    return team_points[1], team_points[2], state_counts


def create_transition_matrix(probs):
    twoPointersMade = probs['twoPointersMade']
    threePointersMade = probs['threePointersMade']
    combinedLostPossession = probs['possessionFailure']
    freeThrows = probs['freeThrows']
    offensiveRebounds = probs['offensiveRebounds']
    ft_pct = probs['ft_pct']

    # Matrix states: Start, Make 2, Make 3, Failed Possession, Free Throw 1, Free Throw 2, And-One, Offensive Rebound, End
    matrix = np.array([
        # Start row
        [0, twoPointersMade, threePointersMade, combinedLostPossession, freeThrows, 0, 0, offensiveRebounds, 0],
        # Make 2
        [0, 0, 0, 0, 0, 0, 0, 0, 1],
        # Make 3
        [0, 0, 0, 0, 0, 0, 0, 0, 1],
        # Failed Possession
        [0, 0, 0, 0, 0, 0, 0, offensiveRebounds, 1 - offensiveRebounds],
        # Free Throw 1
        [0, 0, 0, 0, 0, ft_pct, 0, offensiveRebounds, 1 - ft_pct - offensiveRebounds],
        # Free Throw 2
        [0, 0, 0, 0, 0, 0, 0, offensiveRebounds, 1 - offensiveRebounds],
        # And-One
        [0, 0, 0, 0, 0, 0, 0, offensiveRebounds, ft_pct * 1 + (1 - ft_pct - offensiveRebounds)],
        # Offensive Rebound
        [0, twoPointersMade, threePointersMade, combinedLostPossession, freeThrows, 0, 0, offensiveRebounds, 0],
        # End
        [0, 0, 0, 0, 0, 0, 0, 0, 1]
    ])

    # Normalize each row
    for i in range(len(matrix)):
        row_sum = matrix[i].sum()
        if row_sum > 0:
            matrix[i] /= row_sum

    return matrix


def simulate_matchup(team1_name, team2_name, num_simulations=500):
    print(f"\nSimulating matchup: {team1_name} vs {team2_name}")

    # Get team stats
    teams = getTeams("cbb25.csv")
    team1_stats = findTeam(team1_name, "cbb25.csv")
    team2_stats = findTeam(team2_name, "cbb25.csv")

    if not team1_stats or not team2_stats:
        print("Could not get stats for one or both teams")
        return None

    possessions = (float(team1_stats["ADJ_T"]) + float(team2_stats["ADJ_T"])) / 2  # float division for average

    print(f"Team 1 possessions: {team1_stats['ADJ_T']}")
    print(f"Team 2 possessions: {team2_stats['ADJ_T']}")
    print(f"Possessions: {possessions}")

    print(f"\nCalculating probabilities for {team1_name}:")
    team1_probs = probabilities(team1_stats, team2_stats, possessions)
    print(team1_probs)

    print(f"\nCalculating probabilities for {team2_name}:")
    team2_probs = probabilities(team2_stats, team1_stats, possessions)
    print(team2_probs)

    # Create transition matrices
    team1_matrix = create_transition_matrix(team1_probs)
    team2_matrix = create_transition_matrix(team2_probs)

    # Run simulations
    print(f"\nRunning {num_simulations} simulations...")
    team1_scores = []
    team2_scores = []

    for i in range(num_simulations):
        print(f"\rSimulation {i + 1}/{num_simulations}", end="")
        show_progress = (i == 0)
        score1, score2, statecounts = simulate_game(team1_matrix, team2_matrix, points_per_state, possessions, show_progress)
        team1_scores.append(score1)
        team2_scores.append(score2)
    print(statecounts)
    print()

    # Calculate statistics
    team1_avg = np.mean(team1_scores)
    team2_avg = np.mean(team2_scores)
    team1_std = np.std(team1_scores)
    team2_std = np.std(team2_scores)

    diff_mean = team1_avg - team2_avg
    diff_std = np.sqrt(team1_std**2 + team2_std**2)

    # Probability that Team 1 wins (normal dist. approximation)
    p_team1_wins = 1 - norm.cdf(0, loc=diff_mean, scale=diff_std)

    print(f"\n{team1_avg:.1f} ± {team1_std:.1f}")
    print(f"{team2_avg:.1f} ± {team2_std:.1f}")
    print(f"Probability {team1_name} wins: {p_team1_wins:.2%}")
    print(f"Predicted winner: {team1_name if p_team1_wins > 0.5 else team2_name}")

    return team1_name if p_team1_wins > 0.5 else team2_name
def unweighted_simulate_matchup(team1_name, team2_name, num_simulations=500):
    print(f"\nSimulating matchup: {team1_name} vs {team2_name}")

    # Get team stats
    teams = getTeams("cbb25.csv")
    team1_stats = findTeam(team1_name, "cbb25.csv")
    team2_stats = findTeam(team2_name, "cbb25.csv")

    if not team1_stats or not team2_stats:
        print("Could not get stats for one or both teams")
        return None

    possessions = (float(team1_stats["ADJ_T"]) + float(team2_stats["ADJ_T"])) / 2  # float division for average
    #possessions += float(team1_stats["FTR"]) + float(team1_stats["FTRD"])
    print(f"Team 1 possessions: {team1_stats['ADJ_T']}")
    print(f"Team 2 possessions: {team2_stats['ADJ_T']}")
    print(f"Possessions: {possessions}")

    print(f"\nCalculating probabilities for {team1_name}:")
    team1_probs = probabilitiesUnweighted(team1_stats, team2_stats, possessions)
    print(team1_probs)

    print(f"\nCalculating probabilities for {team2_name}:")
    team2_probs = probabilitiesUnweighted(team2_stats, team1_stats, possessions)
    print(team2_probs)

    # Create transition matrices
    team1_matrix = create_transition_matrix(team1_probs)
    team2_matrix = create_transition_matrix(team2_probs)

    # Run simulations
    print(f"\nRunning {num_simulations} simulations...")
    team1_scores = []
    team2_scores = []

    for i in range(num_simulations):
        print(f"\rSimulation {i + 1}/{num_simulations}", end="")
        show_progress = (i == 0)
        score1, score2, statecounts = simulate_game(team1_matrix, team2_matrix, points_per_state, possessions, show_progress)
        team1_scores.append(score1)
        team2_scores.append(score2)
    print(statecounts)
    print()

    # Calculate statistics
    team1_avg = np.mean(team1_scores)
    team2_avg = np.mean(team2_scores)
    team1_std = np.std(team1_scores)
    team2_std = np.std(team2_scores)

    diff_mean = team1_avg - team2_avg
    diff_std = np.sqrt(team1_std**2 + team2_std**2)

    # Probability that Team 1 wins (normal dist. approximation)
    p_team1_wins = 1 - norm.cdf(0, loc=diff_mean, scale=diff_std)

    print(f"\n{team1_avg:.1f} ± {team1_std:.1f}")
    print(f"{team2_avg:.1f} ± {team2_std:.1f}")
    print(f"Probability {team1_name} wins: {p_team1_wins:.2%}")
    print(f"Predicted winner: {team1_name if p_team1_wins > 0.5 else team2_name}")

    return team1_name if p_team1_wins > 0.5 else team2_name

def main():
    team1 = "florida"
    team2 = "missouri"
    #unweightedResults = unweighted_simulate_matchup(team1,team2)
    results = simulate_matchup(team1, team2)
    return results

if __name__ == "__main__":
    main()
