import csv
from pathlib import Path
from helpers.getTeams import getTeams

def variance(input_csv="cbb25", stats_csv="stats2025", output_csv="stats2025_with_variance.csv"):
    # Step 1: Load base efficiency data
    base_teams = getTeams(input_csv)

    adj_oes = [float(team['ADJOE']) for team in base_teams]
    adj_des = [float(team['ADJDE']) for team in base_teams]

    max_oe = max(adj_oes)
    max_de = max(adj_des)

    # Compute normalized alpha and beta
    for team in base_teams:
        alpha = float(team['ADJOE']) / max_oe
        beta = float(team['ADJDE']) / max_de
        total = alpha + beta
        team['Alpha'] = alpha / total
        team['Beta'] = beta / total

    # Step 2: Create a dictionary for quick team lookup
    alpha_beta_map = {team['Team']: {'Alpha': team['Alpha'], 'Beta': team['Beta']} for team in base_teams}

    # Step 3: Read the stats2025 file and append alpha/beta where matched
    updated_rows = []
    stats_path = Path(__file__).parent.parent / f"{stats_csv}.csv"
    with open(stats_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_name = row['Team Name']
            if team_name in alpha_beta_map:
                row.update(alpha_beta_map[team_name])
            else:
                # Default values if no match found
                row['Alpha'] = 0.5
                row['Beta'] = 0.5
            updated_rows.append(row)

    # Step 4: Write new CSV with Alpha and Beta included
    output_path = Path(__file__).parent.parent / output_csv
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=updated_rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Updated file written to {output_path}")
variance()




