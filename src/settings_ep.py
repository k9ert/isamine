# Initial settings
from .fastapi import app
from fastapi import HTTPException
from pydantic import BaseModel

settings = {
    "do_not_mine_before": 10,
    "do_not_mine_after": 16,
    "max_switch_time_milli": 4000,
}

class Settings(BaseModel):
    do_not_mine_before: int
    do_not_mine_after: int
    max_switch_time_milli: int

@app.get("/settings")
def get_settings():
    return settings

@app.put("/settings")
def update_settings(updated_settings: Settings):
    settings.update(updated_settings.dict())
    return settings