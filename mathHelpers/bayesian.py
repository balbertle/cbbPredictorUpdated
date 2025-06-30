import math
from helpers.getTeams import getTeams
from helperFunctions import data

def probabilities(team_stats, opp_stats, possessions, adjustment_factor=0.25, strength_weight=0.15):
    team = team_stats['Team']
    opp = opp_stats['Team']
    teamData = data(team)
    oppData = data(opp)

    adj_possessions_team = float(team_stats['ADJ_T']) * float(team_stats['G'])
    adj_possessions_opp = float(opp_stats['ADJ_T']) * float(opp_stats['G'])

    # Team shooting and rebounding stats
    team_2p_rate = teamData.fg2 / max(1, adj_possessions_team)
    team_3p_rate = teamData.fg3 / max(1, adj_possessions_team)
    team_orb_rate = teamData.orb / max(1, adj_possessions_team)

    # Opponent defensive stats (allowed)
    opp_2p_allowed = oppData.opp_fg2 / max(1, adj_possessions_opp)
    opp_3p_allowed = oppData.opp_fg3 / max(1, adj_possessions_opp)
    opp_orb_allowed = oppData.opp_orb / max(1, adj_possessions_opp)
    opp_ftr_allowed = float(opp_stats['FTRD']) / 100

    # Performance metrics: BARTHAG and WAB
    team_strength = float(team_stats.get('BARTHAG', 0)) * 5
    opp_strength = float(opp_stats.get('BARTHAG', 0)) * 5
    strength_diff = team_strength - opp_strength

    # Apply linear adjustment toward opponent allowed stats
    def adjust(stat, allowed):
        return stat + adjustment_factor * (allowed - stat)

    twoPointersMade = adjust(team_2p_rate, opp_2p_allowed)
    threePointersMade = adjust(team_3p_rate, opp_3p_allowed)
    offensiveRebounds = adjust(team_orb_rate, opp_orb_allowed)
    freeThrows = opp_ftr_allowed

    missed_shots = teamData.fga - teamData.fg
    possessionFailure = (missed_shots + teamData.tov) / max(1, adj_possessions_team)

    # Normalize offensive components
    components = [twoPointersMade, threePointersMade, possessionFailure, freeThrows, offensiveRebounds]
    total = sum(components)
    if total > 0:
        twoPointersMade /= total
        threePointersMade /= total
        possessionFailure /= total
        freeThrows /= total
        offensiveRebounds /= total

    # Adjust based on team strength difference
    strength_multiplier = 1 + strength_weight * math.tanh(strength_diff)  # bounded, smooth
    twoPointersMade *= strength_multiplier
    threePointersMade *= strength_multiplier
    offensiveRebounds *= strength_multiplier
    freeThrows *= strength_multiplier
    possessionFailure /= strength_multiplier  # failure decreases for stronger teams

    # Renormalize
    components = [twoPointersMade, threePointersMade, possessionFailure, freeThrows, offensiveRebounds]
    total = sum(components)
    if total > 0:
        twoPointersMade /= total
        threePointersMade /= total
        possessionFailure /= total
        freeThrows /= total
        offensiveRebounds /= total

    return {
        'twoPointersMade': twoPointersMade,
        'threePointersMade': threePointersMade,
        'possessionFailure': possessionFailure,
        'freeThrows': freeThrows,
        'offensiveRebounds': offensiveRebounds,
        'ft_pct': teamData.ft_pct
    }
