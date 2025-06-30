import requests
from bs4 import BeautifulSoup
from helperFunctions import getTeams
from scraperFunctions.generalScraper import scrape_team_data, write_to_csv


def main():
    print("\n===== STARTING SCRAPER =====")
    print("Getting list of teams...")
    teams = getTeams()
    print(f"Found {len(teams)} teams to scrape")
    
    scraped_data = []
    for i, team_name in enumerate(teams, 1):
        print(f"\n[{i}/{len(teams)}] Scraping data for {team_name}...")
        team_data = scrape_team_data(team_name)
        if team_data:
            print(f"✓ Successfully scraped data for {team_name}")
            scraped_data.append(team_data)
        else:
            print(f"✗ Failed to scrape data for {team_name}")
    
    print(f"\nSuccessfully scraped data for {len(scraped_data)} out of {len(teams)} teams")
    
    # Write the scraped data to a CSV file
    print("\nWriting data to CSV file...")
    write_to_csv(scraped_data)
    print("CSV file updated successfully")
    
    print("\n===== SCRAPER COMPLETED =====")

if __name__ == "__main__":
    main()