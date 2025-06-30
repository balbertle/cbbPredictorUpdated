import sys
sys.path.append(r'C:\Users\alber\Documents\cbbGamePredictorUpdated')
from helperFunctions import getTeams, data
import requests
from bs4 import BeautifulSoup
import csv
from models import TeamStats
import os

def scrape_team_data(team_name):
    # Construct the URL with the team name
    url = f"https://www.sports-reference.com/cbb/schools/{team_name}/men/2025.html"
    
    # Send a GET request to the website
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 429)
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data for {team_name}. Error: {e}")
        return None
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data for {team_name}. Status code: {response.status_code}")
        return None
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Add new code to get advanced stats using XPath
    team_bpm = 0.0
    try:
        # Use full XPath to find the BPM cell directly
        bpm_cell = soup.select_one('html > body > div:nth-child(4) > div:nth-child(5) > div:nth-child(12) > div:nth-child(5) > div:nth-child(1) > table > tfoot > tr > td:nth-child(25)')
        if bpm_cell:
            # Try multiple ways to get the BPM value
            if bpm_cell.string and bpm_cell.string.strip():
                team_bpm = float(bpm_cell.string.strip())
                print(f"Found team BPM from string: {team_bpm}")
            elif bpm_cell.get('csk'):
                team_bpm = float(bpm_cell.get('csk'))
                print(f"Found team BPM from csk: {team_bpm}")
            elif bpm_cell.get_text(strip=True):
                team_bpm = float(bpm_cell.get_text(strip=True))
                print(f"Found team BPM from text: {team_bpm}")
        else:
            print("BPM cell not found using XPath")
    except (AttributeError, ValueError) as e:
        print(f"Error extracting BPM using XPath: {e}")
        team_bpm = 0.0

    # Scraping data for team
    games_element = soup.find("td", {"data-stat": "games"})
    mp_element = soup.find("td", {"data-stat": "mp"})
    fg_element = soup.find("td", {"data-stat": "fg"})
    fga_element = soup.find("td", {"data-stat": "fga"})
    fg_pct_element = soup.find("td", {"data-stat": "fg_pct"})
    fg2_element = soup.find("td", {"data-stat": "fg2"})
    fg2a_element = soup.find("td", {"data-stat": "fg2a"})
    fg2_pct_element = soup.find("td", {"data-stat": "fg2_pct"})
    fg3_element = soup.find("td", {"data-stat": "fg3"})
    fg3a_element = soup.find("td", {"data-stat": "fg3a"})
    fg3_pct_element = soup.find("td", {"data-stat": "fg3_pct"})
    ft_element = soup.find("td", {"data-stat": "ft"})
    fta_element = soup.find("td", {"data-stat": "fta"})
    ft_pct_element = soup.find("td", {"data-stat": "ft_pct"})
    orb_element = soup.find("td", {"data-stat": "orb"})
    drb_element = soup.find("td", {"data-stat": "drb"})
    trb_element = soup.find("td", {"data-stat": "trb"})
    ast_element = soup.find("td", {"data-stat": "ast"})
    stl_element = soup.find("td", {"data-stat": "stl"})
    blk_element = soup.find("td", {"data-stat": "blk"})
    tov_element = soup.find("td", {"data-stat": "tov"})
    pf_element = soup.find("td", {"data-stat": "pf"})
    pts_element = soup.find("td", {"data-stat": "pts"})
    bpm_element = soup.find("td", {"data-stat": "bpm"})

    # Scraping data for opposing team
    opp_fg_element = soup.find("td", {"data-stat": "opp_fg"})
    opp_fga_element = soup.find("td", {"data-stat": "opp_fga"})
    opp_fg_pct_element = soup.find("td", {"data-stat": "opp_fg_pct"})
    opp_fg2_element = soup.find("td", {"data-stat": "opp_fg2"})
    opp_fg2a_element = soup.find("td", {"data-stat": "opp_fg2a"})
    opp_fg2_pct_element = soup.find("td", {"data-stat": "opp_fg2_pct"})
    opp_fg3_element = soup.find("td", {"data-stat": "opp_fg3"})
    opp_fg3a_element = soup.find("td", {"data-stat": "opp_fg3a"})
    opp_fg3_pct_element = soup.find("td", {"data-stat": "opp_fg3_pct"})
    opp_ft_element = soup.find("td", {"data-stat": "opp_ft"})
    opp_fta_element = soup.find("td", {"data-stat": "opp_fta"})
    opp_ft_pct_element = soup.find("td", {"data-stat": "opp_ft_pct"})
    opp_orb_element = soup.find("td", {"data-stat": "opp_orb"})
    opp_drb_element = soup.find("td", {"data-stat": "opp_drb"})
    opp_trb_element = soup.find("td", {"data-stat": "opp_trb"})
    opp_ast_element = soup.find("td", {"data-stat": "opp_ast"})
    opp_stl_element = soup.find("td", {"data-stat": "opp_stl"})
    opp_blk_element = soup.find("td", {"data-stat": "opp_blk"})
    opp_tov_element = soup.find("td", {"data-stat": "opp_tov"})
    opp_pf_element = soup.find("td", {"data-stat": "opp_pf"})
    opp_pts_element = soup.find("td", {"data-stat": "opp_pts"})

    try:
        # Convert team stats
        games = int(games_element.get_text(strip=True))
        mp = int(mp_element.get_text(strip=True))
        fg = int(fg_element.get_text(strip=True))
        fga = int(fga_element.get_text(strip=True))
        fg_pct = float(fg_pct_element.get_text(strip=True))
        fg2 = int(fg2_element.get_text(strip=True))
        fg2a = int(fg2a_element.get_text(strip=True))
        fg2_pct = float(fg2_pct_element.get_text(strip=True))
        fg3 = int(fg3_element.get_text(strip=True))
        fg3a = int(fg3a_element.get_text(strip=True))
        fg3_pct = float(fg3_pct_element.get_text(strip=True))
        ft = int(ft_element.get_text(strip=True))
        fta = int(fta_element.get_text(strip=True))
        ft_pct = float(ft_pct_element.get_text(strip=True))
        orb = int(orb_element.get_text(strip=True))
        drb = int(drb_element.get_text(strip=True))
        trb = int(trb_element.get_text(strip=True))
        ast = int(ast_element.get_text(strip=True))
        stl = int(stl_element.get_text(strip=True))
        blk = int(blk_element.get_text(strip=True))
        tov = int(tov_element.get_text(strip=True))
        pf = int(pf_element.get_text(strip=True))
        pts = int(pts_element.get_text(strip=True))
        bpm = float(bpm_element.get('data-sort', '0.0')) if bpm_element else 0.0
        print(bpm)
        # Convert opposing team stats
        opp_fg = int(opp_fg_element.get_text(strip=True))
        opp_fga = int(opp_fga_element.get_text(strip=True))
        opp_fg_pct = float(opp_fg_pct_element.get_text(strip=True))
        opp_fg2 = int(opp_fg2_element.get_text(strip=True))
        opp_fg2a = int(opp_fg2a_element.get_text(strip=True))
        opp_fg2_pct = float(opp_fg2_pct_element.get_text(strip=True))
        opp_fg3 = int(opp_fg3_element.get_text(strip=True))
        opp_fg3a = int(opp_fg3a_element.get_text(strip=True))
        opp_fg3_pct = float(opp_fg3_pct_element.get_text(strip=True))
        opp_ft = int(opp_ft_element.get_text(strip=True))
        opp_fta = int(opp_fta_element.get_text(strip=True))
        opp_ft_pct = float(opp_ft_pct_element.get_text(strip=True))
        opp_orb = int(opp_orb_element.get_text(strip=True))
        opp_drb = int(opp_drb_element.get_text(strip=True))
        opp_trb = int(opp_trb_element.get_text(strip=True))
        opp_ast = int(opp_ast_element.get_text(strip=True))
        opp_stl = int(opp_stl_element.get_text(strip=True))
        opp_blk = int(opp_blk_element.get_text(strip=True))
        opp_tov = int(opp_tov_element.get_text(strip=True))
        opp_pf = int(opp_pf_element.get_text(strip=True))
        opp_pts = int(opp_pts_element.get_text(strip=True))
    except ValueError as e:
        print(f"Failed to convert points to integers for {team_name}. Error: {e}")
        return None
        
    efg = (fg + 0.5 * fg3) / fga
    opp_efg = (opp_fg + 0.5 * opp_fg3) / opp_fga
    
    print("finished scrape_team_data")
    print(mp)
    print(fg)
    
    # Return raw data dictionary
    return {
        "Team Name": team_name,
        "Games": games,
        "Minutes Played": mp,
        "Field Goals Made": fg,
        "Field Goals Attempted": fga,
        "Field Goal Percentage": fg_pct,
        "2P Made": fg2,
        "2P Attempted": fg2a,
        "2P Percentage": fg2_pct,
        "3P Made": fg3,
        "3P Attempted": fg3a,
        "3P Percentage": fg3_pct,
        "Free Throws Made": ft,
        "Free Throws Attempted": fta,
        "Free Throw Percentage": ft_pct,
        "Offensive Rebounds": orb,
        "Defensive Rebounds": drb,
        "Total Rebounds": trb,
        "Assists": ast,
        "Steals": stl,
        "Blocks": blk,
        "Turnovers": tov,
        "Personal Fouls": pf,
        "Total Points": pts,
        "Effective Field Goal %": efg,
        "Expected Possessions": tov + fg2a + fg3a + ft // 2.15,
        "Possessions": 0,
        "Box Plus/Minus": team_bpm,
        "Opponent Field Goals Made": opp_fg,
        "Opponent Field Goals Attempted": opp_fga,
        "Opponent Field Goal Percentage": opp_fg_pct,
        "Opponent 2P Made": opp_fg2,
        "Opponent 2P Attempted": opp_fg2a,
        "Opponent 2P Percentage": opp_fg2_pct,
        "Opponent 3P Made": opp_fg3,
        "Opponent 3P Attempted": opp_fg3a,
        "Opponent 3P Percentage": opp_fg3_pct,
        "Opponent Free Throws Made": opp_ft,
        "Opponent Free Throws Attempted": opp_fta,
        "Opponent Free Throw Percentage": opp_ft_pct,
        "Opponent Offensive Rebounds": opp_orb,
        "Opponent Defensive Rebounds": opp_drb,
        "Opponent Total Rebounds": opp_trb,
        "Opponent Assists": opp_ast,
        "Opponent Steals": opp_stl,
        "Opponent Blocks": opp_blk,
        "Opponent Turnovers": opp_tov,
        "Opponent Personal Fouls": opp_pf,
        "Opponent Total Points": opp_pts,
        "Opponent Effective Field Goal %": opp_efg,
        "Box Plus/Minus": team_bpm
    }

def write_to_csv(data, filename="stats2025.csv"):
    # Define the headers
    headers = [
        "Team Name", "Games", "Minutes Played", "Field Goals Made", "Field Goals Attempted", 
        "Field Goal Percentage", "2P Made", "2P Attempted", 
        "2P Percentage", "3P Made", "3P Attempted", "3P Percentage",
        "Free Throws Made", "Free Throws Attempted", "Free Throw Percentage",
        "Offensive Rebounds", "Defensive Rebounds", "Total Rebounds",
        "Assists", "Steals", "Blocks", "Turnovers", "Personal Fouls", "Total Points", "Effective Field Goal %",
        "Expected Possessions", "Possessions",
        "Opponent Field Goals Made", "Opponent Field Goals Attempted", "Opponent Field Goal Percentage",
        "Opponent 2P Made", "Opponent 2P Attempted", "Opponent 2P Percentage",
        "Opponent 3P Made", "Opponent 3P Attempted", "Opponent 3P Percentage",
        "Opponent Free Throws Made", "Opponent Free Throws Attempted", "Opponent Free Throw Percentage",
        "Opponent Offensive Rebounds", "Opponent Defensive Rebounds", "Opponent Total Rebounds",
        "Opponent Assists", "Opponent Steals", "Opponent Blocks", "Opponent Turnovers",
        "Opponent Personal Fouls", "Opponent Total Points", "Opponent Effective Field Goal %",
        "Box Plus/Minus"
    ]
    
    # Write data to file
    try:
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(filename)
        
        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            
            writer.writeheader()
            
            if isinstance(data, dict):
                writer.writerow(data)
            elif isinstance(data, list):
                writer.writerows(data)
                
        print(f"Successfully wrote data to {filename}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")



