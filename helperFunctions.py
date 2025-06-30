import csv
from models import TeamStats

def read_csv(filename="stats2025.csv"):
    """Read the CSV file and return the data as a list of dictionaries."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return []
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

def getTeams():
    return ["auburn", "alabama", "florida", "duke", 
        "tennessee", "houston", "purdue", "texas-am", 
        "st-johns-ny", "iowa-state", "texas-tech", "arizona", "memphis", "kentucky", 
        "wisconsin", "michigan", "michigan-state", "missouri", 
        "marquette", "clemson", "maryland", "mississippi-state", 
        "kansas", "mississippi", "louisville", "mount-st-marys", "baylor", "oregon", 
        "liberty", "akron", "brigham-young", "virginia-commonwealth", "robert-morris",
         "montana", "saint-marys-ca","vanderbilt", "southern-illinois-edwardsville", "gonzaga", 
         "georgia", "clemson", "mcneese-state", "high-point", "illinois", "xavier", "troy",
        "ucla", "utah-state", "wofford", "alabama-state", "creighton", "california-san-diego", "yale",
         "north-carolina", "lipscomb", "new-mexico", "bryant", "norfolk-state", "connecticut", "oklahoma",
        "colorado-state", "grand-canyon", "drake", "north-carolina-wilmington", "arkansas", "nebraska-omaha"
        ,"north-carolina-wilmington"]

def calculate_expected_possessions(row):
    """Calculate expected possessions based on team statistics."""
    # Extract required stats
    fg2a = int(row['2P Attempted'])
    fg3a = int(row['3P Attempted'])
    fta = int(row['Free Throws Attempted'])
    orb = int(row['Offensive Rebounds'])
    tov = int(row['Turnovers'])
    games = int(row['Games'])
    
    # Calculate possessions
    fga = fg2a + fg3a
    estimated_possessions = fga + 0.44 * fta - orb + tov
    possessions_per_game = estimated_possessions / max(1, games)
    
    return possessions_per_game

def data(team_name):
    """Get the data for a specific team."""
    try:
        data_list = read_csv()
        if not data_list:
            print("No data found in CSV file")
            return None
        
        for row in data_list:
            if row['Team Name'].lower() == team_name.lower():
                # Get expected possessions if available, otherwise calculate it
                if 'Expected Possessions' in row and row['Expected Possessions']:
                    expected_possessions = float(row['Expected Possessions'])
                else:
                    expected_possessions = calculate_expected_possessions(row)
                
                bpm = float(row['Box Plus/Minus'])
                
                # Convert string values to appropriate types
                return TeamStats(
                    team_name=row['Team Name'],
                    games=int(row['Games']),
                    mp=int(row['Minutes Played']),
                    fg=int(row['Field Goals Made']),
                    fga=int(row['Field Goals Attempted']),
                    fg_pct=float(row['Field Goal Percentage']),
                    fg2=int(row['2P Made']),
                    fg2a=int(row['2P Attempted']),
                    fg2_pct=float(row['2P Percentage']),
                    fg3=int(row['3P Made']),
                    fg3a=int(row['3P Attempted']),
                    fg3_pct=float(row['3P Percentage']),
                    ft=int(row['Free Throws Made']),
                    fta=int(row['Free Throws Attempted']),
                    ft_pct=float(row['Free Throw Percentage']),
                    orb=int(row['Offensive Rebounds']),
                    drb=int(row['Defensive Rebounds']),
                    trb=int(row['Total Rebounds']),
                    ast=int(row['Assists']),
                    stl=int(row['Steals']),
                    blk=int(row['Blocks']),
                    tov=int(row['Turnovers']),
                    pf=int(row['Personal Fouls']),
                    pts=int(row['Total Points']),
                    efg=float(row['Effective Field Goal %']),
                    expected_possessions=expected_possessions,
                    possessions=float(row['Possessions']), 
                    bpm=bpm,
                    opp_fg=int(row['Opponent Field Goals Made']),
                    opp_fga=int(row['Opponent Field Goals Attempted']),
                    opp_fg_pct=float(row['Opponent Field Goal Percentage']),
                    opp_fg2=int(row['Opponent 2P Made']),
                    opp_fg2a=int(row['Opponent 2P Attempted']),
                    opp_fg2_pct=float(row['Opponent 2P Percentage']),
                    opp_fg3=int(row['Opponent 3P Made']),
                    opp_fg3a=int(row['Opponent 3P Attempted']),
                    opp_fg3_pct=float(row['Opponent 3P Percentage']),
                    opp_ft=int(row['Opponent Free Throws Made']),
                    opp_fta=int(row['Opponent Free Throws Attempted']),
                    opp_ft_pct=float(row['Opponent Free Throw Percentage']),
                    opp_orb=int(row['Opponent Offensive Rebounds']),
                    opp_drb=int(row['Opponent Defensive Rebounds']),
                    opp_trb=int(row['Opponent Total Rebounds']),
                    opp_ast=int(row['Opponent Assists']),
                    opp_stl=int(row['Opponent Steals']),
                    opp_blk=int(row['Opponent Blocks']),
                    opp_tov=int(row['Opponent Turnovers']),
                    opp_pf=int(row['Opponent Personal Fouls']),
                    opp_pts=int(row['Opponent Total Points']),
                    opp_efg=float(row['Opponent Effective Field Goal %'])
                )
        print(f"Team '{team_name}' not found in CSV file")
        return None
    except Exception as e:
        print(f"Error getting data for team {team_name}: {e}")
        return None