import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from schemas import Team, Match, MatchEvent, StandingRow, Prediction

app = FastAPI(title="SCORETURK API", description="Live Football Worldwide")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "SCORETURK Backend Running"}


# ---- Sample content for wireframes & UI prototyping ----

def sample_match(now: datetime) -> Match:
    home = Team(name="Barcelona", short_name="BAR", primary_color="#A50044", secondary_color="#004D98")
    away = Team(name="Real Madrid", short_name="RMA", primary_color="#FEBE10", secondary_color="#FFFFFF")
    events = [
        MatchEvent(minute=12, type="goal", team="home", player="Lewandowski", assist="Pedri"),
        MatchEvent(minute=33, type="card", team="away", player="Rüdiger", detail="Yellow"),
        MatchEvent(minute=45, type="ht"),
        MatchEvent(minute=57, type="goal", team="away", player="Vinícius Jr", assist="Bellingham"),
        MatchEvent(minute=78, type="goal", team="home", player="Gündoğan"),
    ]
    start = now - timedelta(minutes=60)
    return Match(
        league="La Liga",
        status="LIVE",
        start_time=start,
        home_team=home,
        away_team=away,
        home_score=2,
        away_score=1,
        events=events,
        win_probability=[58.0, 22.0, 20.0],
    )


@app.get("/api/live", response_model=List[Match])
def get_live_matches():
    now = datetime.utcnow()
    return [sample_match(now)]


@app.get("/api/match/{match_id}", response_model=Match)
def get_match(match_id: str):
    # For wireframes, return the sample match regardless of ID
    return sample_match(datetime.utcnow())


@app.get("/api/standings", response_model=List[StandingRow])
def get_standings(league: str = "La Liga"):
    teams = [
        Team(name="Barcelona", short_name="BAR", primary_color="#A50044", secondary_color="#004D98"),
        Team(name="Real Madrid", short_name="RMA", primary_color="#FEBE10", secondary_color="#FFFFFF"),
        Team(name="Atletico", short_name="ATM", primary_color="#C72B2B", secondary_color="#0E1E2F"),
    ]
    table = [
        StandingRow(team=teams[0], played=28, won=19, draw=6, lost=3, gf=59, ga=22, gd=37, points=63),
        StandingRow(team=teams[1], played=28, won=18, draw=7, lost=3, gf=55, ga=24, gd=31, points=61),
        StandingRow(team=teams[2], played=28, won=17, draw=6, lost=5, gf=49, ga=28, gd=21, points=57),
    ]
    return table


@app.get("/api/predictions", response_model=List[Prediction])
def get_predictions():
    preds = [
        Prediction(match_id="bar-rma-001", home_win=0.58, draw=0.22, away_win=0.20, suggested_bets=["Home Win", "Over 2.5"]),
    ]
    return preds


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
