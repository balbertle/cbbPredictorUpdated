import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Section 1: Import all necessary simulation and data functions ---
# Note the import from 'log5sim' (or whatever you named your main simulator file)
from mathHelpers.log5sim import simulate_matchup 
from helpers.getTeams import getTeams
from helpers.findTeam import findTeam
from helperFunctions import data
from helpers.prepare_stats import prepare_team_stats, calculate_league_averages
PYTHAGOREAN_EXPONENT = 4.386 # backtested variable

# --- Section 2: Define the Tournament Bracket ---
initial_matchups = [
    # West Region
    ("florida", "norfolk-state"), ("connecticut", "oklahoma"), ("maryland", "grand-canyon"),
    ("memphis", "colorado-state"), ("missouri", "drake"), ("texas-tech", "north-carolina-wilmington"),
    ("kansas", "arkansas"), ("st-johns-ny", "nebraska-omaha"),
    # South Region
    ("auburn", "alabama-state"), ("louisville", "creighton"), ("michigan", "california-san-diego"),
    ("texas-am", "yale"), ("mississippi", "north-carolina"), ("iowa-state", "lipscomb"),
    ("marquette", "new-mexico"), ("michigan-state", "bryant"),
    # Midwest Region
    ("houston", "southern-illinois-edwardsville"), ("gonzaga", "georgia"), ("clemson", "mcneese-state"),
    ("purdue", "high-point"), ("illinois", "xavier"), ("kentucky", "troy"),
    ("ucla", "utah-state"), ("tennessee", "wofford"),
    # East Region
    ("duke", "mount-st-marys"), ("mississippi-state", "baylor"), ("oregon", "liberty"),
    ("arizona", "akron"), ("virginia-commonwealth", "brigham-young"), ("wisconsin", "montana"),
    ("saint-marys-ca", "vanderbilt"), ("alabama", "robert-morris"),
]


# --- Section 3: Modified Simulation Functions for Monte Carlo Analysis ---
def simulate_single_game(team1_name, team2_name, all_teams_csv, league_averages, exponent):
    """
    Helper function to simulate just one game and return the winner.
    """
    team1_csv = findTeam(team1_name, all_teams_csv)
    team1_obj = data(team1_name)
    team2_csv = findTeam(team2_name, all_teams_csv)
    team2_obj = data(team2_name)

    if not all((team1_csv, team1_obj, team2_csv, team2_obj)):
        return team1_name if (team1_csv and team1_obj) else team2_name
    
    team1_stats = prepare_team_stats(team1_csv, team1_obj)
    team2_stats = prepare_team_stats(team2_csv, team2_obj)

    if not team1_stats or not team2_stats:
        return team1_name if team1_stats else team2_name
        
    return simulate_matchup(
        team1_name, team1_stats,
        team2_name, team2_stats,
        league_averages,
        exponent=exponent
    )
def run_monte_carlo_tournament(num_tournaments, initial_matchups, all_teams_csv, league_averages, exponent):
    """
    Runs the entire tournament simulation `num_tournaments` times.
    """
    matchup_win_counts = defaultdict(lambda: defaultdict(int))
    
    print(f"--- Running {num_tournaments} Full Tournament Simulations ---")
    for i in range(num_tournaments):
        print(f"\rSimulating Tournament {i + 1}/{num_tournaments}", end="")
        current_winners = [team for matchup in initial_matchups for team in matchup]
        while len(current_winners) > 1:
            next_round_winners = []
            current_matchups = list(zip(current_winners[0::2], current_winners[1::2]))
            for team1, team2 in current_matchups:
                # Pass the exponent to the game simulator
                winner = simulate_single_game(team1, team2, all_teams_csv, league_averages, exponent)
                next_round_winners.append(winner)
                matchup_key = tuple(sorted((team1, team2)))
                matchup_win_counts[matchup_key][winner] += 1
            current_winners = next_round_winners
    
    print("\n\n--- Monte Carlo Simulation Complete ---")
    return matchup_win_counts

def determine_most_probable_bracket(initial_matchups, matchup_win_counts):
    """
    Analyzes the win counts to build the single most probable bracket outcome.
    """
    print("Building most probable bracket...")
    all_rounds_winners = []
    
    current_winners = [team for matchup in initial_matchups for team in matchup]
    all_rounds_winners.append(current_winners)
    
    while len(current_winners) > 1:
        next_round_winners = []
        current_matchups = list(zip(current_winners[0::2], current_winners[1::2]))
        
        for team1, team2 in current_matchups:
            matchup_key = tuple(sorted((team1, team2)))
            win_counts = matchup_win_counts.get(matchup_key, {team1: 1, team2: 0}) # Default to team1 winning if no data
            
            # Determine the winner by seeing who won the most times
            winner = max(win_counts, key=win_counts.get)
            next_round_winners.append(winner)
            
        current_winners = next_round_winners
        all_rounds_winners.append(current_winners)
        
    print(f"\n🎉 Most Probable Tournament Champion: {current_winners[0]}")
    return all_rounds_winners

# --- Section 4: Your Visualization Function (Unchanged) ---
def visualize_bracket(rounds):
    # ... (This function is perfect as is)
    G = nx.DiGraph(); labels = {}; pos = {}; y_gap = 1.5
    for r, winners in enumerate(rounds):
        x = r
        for i, team in enumerate(winners):
            node = f"{r}-{i}"; G.add_node(node, label=team); pos[node] = (x, -i * y_gap)
            labels[node] = team.replace('-', ' ').title()
    for r in range(len(rounds) - 1):
        for i in range(0, len(rounds[r]), 2):
            parent1 = f"{r}-{i}"; parent2 = f"{r}-{i+1}"; child = f"{r+1}-{i//2}"
            G.add_edge(parent1, child); G.add_edge(parent2, child)
    plt.figure(figsize=(20, 30)); nx.draw(G, pos, with_labels=False, node_size=3000, node_color='skyblue', node_shape='s')
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight='bold')
    plt.title("Most Probable NCAA Tournament Outcome", fontsize=20); plt.axis('off'); plt.tight_layout(); plt.show()


# --- Section 5: Main Execution Block ---
def main():
    """Main execution block for the Monte Carlo tournament simulation."""
    # ... (data loading) ...
    all_teams_csv = getTeams("cbb25.csv")
    if not all_teams_csv: return
    league_averages = calculate_league_averages(all_teams_csv, data)
    
    # Run the Monte Carlo simulation, passing the exponent
    matchup_results = run_monte_carlo_tournament(
        num_tournaments=1, 
        initial_matchups=initial_matchups, 
        all_teams_csv="cbb25.csv", 
        league_averages=league_averages,
        exponent=PYTHAGOREAN_EXPONENT
    )
    
    most_probable_rounds = determine_most_probable_bracket(initial_matchups, matchup_results)
    visualize_bracket(most_probable_rounds)

if __name__ == "__main__":
    main()