from dataclasses import dataclass

@dataclass
class TeamStats:
    team_name: str
    games: int
    # Team stats
    mp: int
    fg: int
    fga: int
    fg_pct: float
    fg2: int
    fg2a: int
    fg2_pct: float
    fg3: int
    fg3a: int
    fg3_pct: float
    ft: int
    fta: int
    ft_pct: float
    orb: int
    drb: int
    trb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    pts: int
    efg: float
    expected_possessions: int
    possessions: int
    bpm: float
    # Opponent stats
    opp_fg: int
    opp_fga: int
    opp_fg_pct: float
    opp_fg2: int
    opp_fg2a: int
    opp_fg2_pct: float
    opp_fg3: int
    opp_fg3a: int
    opp_fg3_pct: float
    opp_ft: int
    opp_fta: int
    opp_ft_pct: float
    opp_orb: int
    opp_drb: int
    opp_trb: int
    opp_ast: int
    opp_stl: int
    opp_blk: int
    opp_tov: int
    opp_pf: int
    opp_pts: int
    opp_efg: float

    def to_tuple(self):
        return (
            self.team_name, self.games, self.mp, self.fg, self.fga, self.fg_pct, self.fg2, self.fg2a, self.fg2_pct,
            self.fg3, self.fg3a, self.fg3_pct, self.ft, self.fta, self.ft_pct, self.orb, self.drb,
            self.trb, self.ast, self.stl, self.blk, self.tov, self.pf, self.pts, self.efg, self.expected_possessions, self.possessions,
            self.bpm,
            self.opp_fg, self.opp_fga, self.opp_fg_pct, self.opp_fg2, self.opp_fg2a, self.opp_fg2_pct,
            self.opp_fg3, self.opp_fg3a, self.opp_fg3_pct, self.opp_ft, self.opp_fta, self.opp_ft_pct,
            self.opp_orb, self.opp_drb, self.opp_trb, self.opp_ast, self.opp_stl, self.opp_blk,
            self.opp_tov, self.opp_pf, self.opp_pts, self.opp_efg
        ) 