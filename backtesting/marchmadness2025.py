
#from mathHelpers.simulator import simulate_matchup
from mathHelpers.log5sim import simulate_matchup
import networkx as nx
import matplotlib.pyplot as plt


# Initial matchups: Round of 64 (2025)
initial_matchups = [
    # West Region
    ("florida", "norfolk-state"),         # 1 vs 16
    ("connecticut", "oklahoma"),        # 8 vs 9
    ("maryland", "grand-canyon"),       # 5 vs 12
    ("memphis", "colorado-state"),        # 4 vs 13
    ("missouri", "drake"),   # 6 vs 11
    ("texas-tech", "north-carolina-wilmington"),             # 3 vs 14
    ("kansas", "arkansas"),              # 7 vs 10
    ("st-johns-ny", "nebraska-omaha"),  # 2 vs 15
    # South Region (16 teams)
    ("auburn", "alabama-state"),          # 1 vs 16
    ("louisville", "creighton"),        # 8 vs 9
    ("michigan", "california-san-diego"),       # 5 vs 12
    ("texas-am", "yale"),              # 4 vs 13
    ("mississippi", "north-carolina"), # 6 vs 11
    ("iowa-state", "lipscomb"),           # 3 vs 14
    ("marquette", "new-mexico"),        # 7 vs 10
    ("michigan-state", "bryant"),         # 2 vs 15
 # Midwest Region (16 teams)
    ("houston", "southern-illinois-edwardsville"),    # 1 vs 16
    ("gonzaga", "georgia"),             # 8 vs 9
    ("clemson", "mcneese-state"),           # 5 vs 12
    ("purdue", "high-point"),               # 4 vs 13
    ("illinois", "xavier"),             # 6 vs 11
    ("kentucky", "troy"),               # 3 vs 14
    ("ucla", "utah-state"),           # 7 vs 10
    ("tennessee", "wofford"),        # 2 vs 15
    # East Region (16 teams)
    ("duke", "mount-st-marys"),       # 1 vs 16
    ("mississippi-state", "baylor"),      # 8 vs 9
    ("oregon", "liberty"),       # 5 vs 12
    ("arizona", "akron"),               # 4 vs 13
    ("virginia-commonwealth", "brigham-young"),                    # 6 vs 11
    ("wisconsin", "montana"),           # 3 vs 14
    ("saint-marys-ca", "vanderbilt"),    # 7 vs 10
    ("alabama", "robert-morris"),              # 2 vs 15
]


def simulate_round(matchups):
    winners = []
    for team1, team2 in matchups:
        winner = simulate_matchup(team1, team2)
        print(f"{team1} vs {team2} → Winner: {winner}")
        winners.append(winner)
    return winners

def simulate_tournament(initial_matchups):
    round_num = 1
    current_matchups = initial_matchups
    rounds = []

    while len(current_matchups) > 1:
        print(f"\n🏀 Round {round_num}")
        winners = simulate_round(current_matchups)
        rounds.append(winners)
        # Create next round matchups
        current_matchups = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
        round_num += 1

    # Final round
    print(f"\n🏆 Final Match")
    final_winner = simulate_round(current_matchups)[0]
    print(f"\n🎉 Tournament Champion: {final_winner}")

    return rounds

# Run the simulation
rounds = simulate_tournament(initial_matchups)

def visualize_bracket(rounds):
    G = nx.DiGraph()
    label_pos = {}
    pos = {}
    y_gap = 1.5

    # Build graph nodes for each round
    for r, winners in enumerate(rounds):
        x = r
        for i, team in enumerate(winners):
            node = f"{r}-{i}"
            G.add_node(node, label=team)
            pos[node] = (x, -i * y_gap)
            label_pos[node] = team

    # Add edges from round r to r+1
    for r in range(len(rounds) - 1):
        for i in range(0, len(rounds[r]), 2):
            parent1 = f"{r}-{i}"
            parent2 = f"{r}-{i+1}"
            child = f"{r+1}-{i//2}"
            G.add_edge(parent1, child)
            G.add_edge(parent2, child)

    nx.draw(G, pos, with_labels=False, node_size=2000, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, labels=label_pos, font_size=8)
    plt.title("March Madness Bracket Visualization")
    plt.axis('off')
    plt.show()
visualize_bracket(rounds)