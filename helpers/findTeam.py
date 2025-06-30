from helpers.getTeams import getTeams

def findTeam(teamName, file):
    teams = getTeams(file)
    for team in teams: 
        if team['Team'] == teamName:
            return team
        
