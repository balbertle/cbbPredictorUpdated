# bayesian.py
import math

def log5(stat_a, stat_b, league_avg_stat):
    """
    Calculates the expected outcome of a matchup between two entities using the Log5 formula.
    This helper function is correct and does not need changes.
    """
    denominator = stat_a + stat_b - 2 * stat_a * stat_b
    if denominator == 0:
        return 0.5
    return (stat_a - stat_a * stat_b) / denominator

def calculate_four_factors_probabilities(team_stats, opp_stats, league_avg_stats):
    """
    CORRECTED: This function now correctly frames all defensive stats as "success rates"
    before applying the Log5 formula to adjust event OUTCOMES.
    """
    # --- 1. Use Base Event Probabilities Directly ---
    # The probability of a turnover, foul, or shot is determined by the team's style.
    # We take these directly from the pre-calculated, normalized stats.
    p_turnover = team_stats['p_turnover']
    p_shooting_foul = team_stats['p_shooting_foul']
    p_fga = team_stats['p_fga']

    # --- 2. Adjust OUTCOME Probabilities Based on Opponent ---

    # A) Adjust Shooting Success:
    # First, calculate the team's base eFG% from its 2P% and 3P%
    team_efg = (team_stats['2P_pct'] * (1 - team_stats['3PAr'])) + (team_stats['3P_pct'] * 1.5 * team_stats['3PAr'])
    
    # We compare the offense's ability to score vs. the defense's ability to prevent scores.
    adj_efg = log5(team_efg, 1 - opp_stats['def_eFG_pct'], 1 - league_avg_stats['eFG_pct'])
    
    # Create a scaling factor to adjust the team's 2P% and 3P% up or down.
    scaling_factor = adj_efg / team_efg if team_efg > 0 else 1.0
    p_make_2 = team_stats['2P_pct'] * scaling_factor
    p_make_3 = team_stats['3P_pct'] * scaling_factor

    # B) Adjust Rebounding Success:
    # The defense's success rate at rebounding is (1 - their allowed ORB%).
    adj_orb_pct = log5(team_stats['ORB_pct'], 1 - opp_stats['def_ORB_pct'], league_avg_stats['ORB_pct'])

    # --- 3. Split Base Event Probabilities into Components ---
    # We use the UNADJUSTED p_fga and p_shooting_foul for this.
    three_point_attempt_rate = team_stats['3PAr']
    p_fga_3 = p_fga * three_point_attempt_rate
    p_fga_2 = p_fga * (1 - three_point_attempt_rate)

    p_and_one = 0.03 * p_shooting_foul 
    p_shooting_foul -= p_and_one
    p_foul_on_3 = p_shooting_foul * three_point_attempt_rate
    p_foul_on_2 = p_shooting_foul * (1 - three_point_attempt_rate)
    
    # --- 4. Return the Final Dictionary ---
    return {
        # Base event probabilities (unadjusted)
        'p_fga_2': p_fga_2,
        'p_fga_3': p_fga_3,
        'p_turnover': p_turnover,
        'p_foul_on_2': p_foul_on_2,
        'p_foul_on_3': p_foul_on_3,
        'p_and_one': p_and_one,
        
        # Outcome probabilities (adjusted for opponent)
        'p_make_2': min(p_make_2, 0.95), # Cap probability
        'p_make_3': min(p_make_3, 0.95), # Cap probability
        'p_ft_make': team_stats['FT_pct'], # FT% is considered independent of opponent
        'p_offensive_rebound': adj_orb_pct
    }
