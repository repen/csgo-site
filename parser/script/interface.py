from dataclasses import dataclass, field

@dataclass
class IFixture:
    m_id:int
    m_timestamp:int = field(repr=False)
    m_team1:str = field(repr=False)
    m_team2:str = field(repr=False)
    m_league:str = field(repr=False)

@dataclass
class IMarket:
    m_id:int
    c_id:int
    m_snapshot_time:int
    left_value:int
    name:str
    right_value:int

@dataclass
class IResult:
    c_id:int
    winner:str
    score:str


@dataclass
class IKoef:
    m_id:int
    m_snapshot_time:int
    left_value:str
    market_name:str
    right_value:str
    left_percent:str
    right_percent:str



