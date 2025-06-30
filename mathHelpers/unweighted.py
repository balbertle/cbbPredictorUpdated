import math
from helpers.getTeams import getTeams
from helperFunctions import data

def probabilitiesUnweighted(team_stats, opp_stats, possessions):
    team = team_stats['Team']
    opp = opp_stats['Team']
    teamData = data(team)
    oppData = data(opp)

    adj_possessions_team = float(team_stats['ADJ_T']) * teamData.games
    # Team shooting rates per possession
    team_2p_rate = teamData.fg2 / max(1, adj_possessions_team)
    team_3p_rate = teamData.fg3 / max(1, adj_possessions_team)
    offensiveRebounds = teamData.orb / max(1, adj_possessions_team)
    freeThrows = float(opp_stats['FTRD']) / 200
    missed_shots = teamData.fga - teamData.fg
    possessionFailure = (missed_shots + teamData.tov) / max(1, adj_possessions_team)
    print(team_2p_rate)
    print(team_3p_rate)
    print(freeThrows)
    print(offensiveRebounds)
    print(possessionFailure)


    # Normalize all components to sum to 1
    components = [team_2p_rate, team_3p_rate, possessionFailure, freeThrows, offensiveRebounds]
    total = sum(components)
    if total > 0:
        team_2p_rate /= total
        team_3p_rate /= total
        possessionFailure /= total
        freeThrows /= total
        offensiveRebounds /= total

    return {
        'twoPointersMade': team_2p_rate,
        'threePointersMade': team_3p_rate,
        'possessionFailure': possessionFailure,
        'freeThrows': freeThrows,
        'offensiveRebounds': offensiveRebounds,
        'ft_pct': teamData.ft_pct
    }

# Example usage
teams = getTeams("cbb25")
team1 = teams[0]
team2 = teams[1]
possessions = (float(team1['ADJ_T']) + float(team2['ADJ_T'])) / 2
print(probabilitiesUnweighted(team1, team2, possessions))
