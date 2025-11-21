"""
Database Schemas for SCORETURK

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
These are used for validation and to power potential persistence for live data
(e.g., teams, matches, events, players). For the wireframe phase we may return
sample payloads from the API without writing to the database, but schemas are
defined here to enable persistence later without structural changes.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Team(BaseModel):
    name: str = Field(..., description="Team name")
    short_name: Optional[str] = Field(None, description="Short code like FCB, MCI")
    primary_color: Optional[str] = Field(None, description="Hex color for UI adaptation")
    secondary_color: Optional[str] = Field(None, description="Secondary hex color")
    crest_url: Optional[str] = Field(None, description="URL to team crest")
    league: Optional[str] = Field(None, description="League name")


class Player(BaseModel):
    name: str
    number: Optional[int] = None
    position: Optional[str] = None
    team_id: Optional[str] = None
    rating: Optional[float] = None


class MatchEvent(BaseModel):
    minute: int = Field(..., ge=0)
    type: str = Field(..., description="goal|card|var|sub|shot|offside|ht|ft")
    team: Optional[str] = Field(None, description="home|away")
    player: Optional[str] = None
    assist: Optional[str] = None
    detail: Optional[str] = None


class Match(BaseModel):
    league: str
    status: str = Field(..., description="NS|LIVE|HT|FT|POSTPONED")
    start_time: datetime
    home_team: Team
    away_team: Team
    home_score: int = 0
    away_score: int = 0
    events: List[MatchEvent] = []
    win_probability: Optional[List[float]] = Field(
        default=None, description="Array [home%, draw%, away%]"
    )


class StandingRow(BaseModel):
    team: Team
    played: int
    won: int
    draw: int
    lost: int
    gf: int
    ga: int
    gd: int
    points: int


class Prediction(BaseModel):
    match_id: str
    home_win: float
    draw: float
    away_win: float
    suggested_bets: Optional[List[str]] = None
