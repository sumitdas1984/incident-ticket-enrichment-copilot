# models/common.py — Shared Pydantic models used across endpoints

from datetime import datetime

from pydantic import BaseModel, Field


class TimeRange(BaseModel):
    """Inclusive time window used by analytics endpoints."""

    start_time: datetime = Field(..., description="Window start (inclusive).")
    end_time: datetime = Field(..., description="Window end (inclusive).")