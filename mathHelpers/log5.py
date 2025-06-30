# bayesian.py
import math

def log5(stat_a, stat_b, league_avg_stat):
    if (stat_a + stat_b - 2 * stat_a * stat_b) == 0:
        return (stat_a + stat_b) / 2
    return (stat_a - stat_a * stat_b) / (stat_a + stat_b - 2 * stat_a * stat_b)

def calculate_four_factors_probabilities(team_stats, opp_stats, league_avg_stats):
    """
    Adjusts the pre-calculated, normalized probabilities from team_stats using the Log5 formula.
    """
    # 1. Adjust the core, mutually exclusive probabilities
    adj_p_turnover = log5(team_stats['p_turnover'], 1 - opp_stats['def_TOV_pct'], 1-league_avg_stats['TOV_pct'])
    adj_p_shooting_foul = log5(team_stats['p_shooting_foul'], opp_stats['def_FTR'], league_avg_stats['FTR'])
    adj_p_fga = log5(team_stats['p_fga'], 1-opp_stats['def_eFG_pct'], 1-league_avg_stats['eFG_pct'])

    # 2. Re-normalize the adjusted probabilities so they sum to 1.0
    total_prob = adj_p_turnover + adj_p_shooting_foul + adj_p_fga
    p_turnover = adj_p_turnover / total_prob
    p_shooting_foul = adj_p_shooting_foul / total_prob
    p_fga = adj_p_fga / total_prob

    # 3. Adjust success and other rates
    adj_orb_pct = log5(team_stats['ORB_pct'], 1 - opp_stats['def_ORB_pct'], league_avg_stats['ORB_pct'])
    
    team_efg = (team_stats['2P_pct'] * (1 - team_stats['3PAr'])) + (team_stats['3P_pct'] * 1.5 * team_stats['3PAr'])
    adj_efg = log5(team_efg, opp_stats['def_eFG_pct'], league_avg_stats['eFG_pct'])
    
    scaling_factor = adj_efg / team_efg if team_efg > 0 else 1.0
    p_make_2 = team_stats['2P_pct'] * scaling_factor
    p_make_3 = team_stats['3P_pct'] * scaling_factor
    
    # 4. Split FGA and Foul probabilities into their components
    three_point_attempt_rate = team_stats['3PAr']
    p_fga_3 = p_fga * three_point_attempt_rate
    p_fga_2 = p_fga * (1 - three_point_attempt_rate)

    p_and_one = 0.03 * p_shooting_foul 
    p_shooting_foul -= p_and_one
    p_foul_on_3 = p_shooting_foul * three_point_attempt_rate
    p_foul_on_2 = p_shooting_foul * (1 - three_point_attempt_rate)
    
    return {
        'p_fga_2': p_fga_2, 'p_fga_3': p_fga_3, 'p_turnover': p_turnover,
        'p_foul_on_2': p_foul_on_2, 'p_foul_on_3': p_foul_on_3, 'p_and_one': p_and_one,
        'p_make_2': min(p_make_2, 0.95), 'p_make_3': min(p_make_3, 0.95),
        'p_ft_make': team_stats['FT_pct'], 'p_offensive_rebound': adj_orb_pct
    }