# stats_calculator.py


def prepare_team_stats(team_csv_data, team_object_data):
    """
    Calculates true, normalized, and mutually exclusive per-possession event rates.
    """
    try:
        # ... (all existing logic for calculating possessions and probabilities) ...
        possessions = (
            team_object_data.fga + 0.44 * team_object_data.fta - 
            team_object_data.orb + team_object_data.tov
        )
        if possessions == 0: raise ValueError("Calculated possessions is zero.")
        rate_tov = team_object_data.tov / possessions
        rate_fga = team_object_data.fga / possessions
        rate_ft_trip = (team_object_data.fta * 0.44) / possessions
        total_event_rate = rate_tov + rate_fga + rate_ft_trip
        if total_event_rate == 0: raise ValueError("Total event rate is zero.")
        p_turnover = rate_tov / total_event_rate
        p_fga = rate_fga / total_event_rate
        p_shooting_foul = rate_ft_trip / total_event_rate
        opp_possessions = (
            team_object_data.opp_fga + 0.44 * team_object_data.opp_fta - 
            team_object_data.opp_orb + team_object_data.opp_tov
        )
        
        stats = {
            # ... (all the other stats like p_turnover, 2P_pct, etc.) ...
            'p_turnover': p_turnover, 'p_shooting_foul': p_shooting_foul, 'p_fga': p_fga,
            '2P_pct': team_object_data.fg2_pct, '3P_pct': team_object_data.fg3_pct,
            'FT_pct': team_object_data.ft_pct,
            '3PAr': team_object_data.fg3a / team_object_data.fga if team_object_data.fga > 0 else 0,
            'ORB_pct': team_object_data.orb / (team_object_data.orb + team_object_data.opp_drb),
            'def_eFG_pct': team_object_data.opp_efg,
            'def_TOV_pct': team_object_data.opp_tov / opp_possessions if opp_possessions > 0 else 0,
            'poss_per_g': float(team_csv_data['ADJ_T']),
            'def_ORB_pct': float(team_csv_data['DRB']) / 100.0,
            'def_FTR': float(team_csv_data['FTRD']) / 100.0,
            'ADJOE': float(team_csv_data['ADJOE']),
            'ADJDE': float(team_csv_data['ADJDE']),
            'BARTHAG': float(team_csv_data['BARTHAG'])
        }
        return stats

    except (AttributeError, KeyError, ZeroDivisionError, ValueError, TypeError) as e:
        team_name = getattr(team_object_data, 'team_name', 'N/A')
        print(f"ERROR processing data for {team_name}: {e}. Check source data.")
        return None


def calculate_league_averages(all_teams_raw_data, get_team_obj_func):
    league_totals = {'eFG_pct': 0, 'TOV_pct': 0, 'ORB_pct': 0, 'FTR': 0, 'PPG': 0}
    num_teams = 0
    for team_csv in all_teams_raw_data:
        try:
            league_totals['eFG_pct'] += float(team_csv['EFG_O'])
            league_totals['TOV_pct'] += float(team_csv['TOR'])
            league_totals['ORB_pct'] += float(team_csv['ORB'])
            league_totals['FTR'] += float(team_csv['FTR'])
            league_totals['PPG'] += float(team_csv['ADJOE']) * 100
            num_teams += 1
        except (ValueError, KeyError): continue
    league_averages = {key: (total / num_teams) / 100.0 for key, total in league_totals.items()}
    print("\nCalculated League Averages (from CSV):")
    for key, val in league_averages.items(): print(f"  {key}: {val:.3f}")
    return league_averages