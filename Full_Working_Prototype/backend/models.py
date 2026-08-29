from sqlalchemy import String, Float, Boolean, JSON, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import datetime

class VisionLog(Base):
    __tablename__ = "vision_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    intersection_id: Mapped[str] = mapped_column(String)
    zone: Mapped[str] = mapped_column(String)
    counts: Mapped[dict] = mapped_column(JSON)
    platoon_detected: Mapped[bool] = mapped_column(Boolean)
    tracked_objects: Mapped[dict] = mapped_column(JSON)

class TomTomLog(Base):
    __tablename__ = "tomtom_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    segment_id: Mapped[str] = mapped_column(String)
    current_speed_kmh: Mapped[float] = mapped_column(Float)
    free_flow_speed_kmh: Mapped[float] = mapped_column(Float)
    congestion_ratio: Mapped[float] = mapped_column(Float)

class SumoStateLog(Base):
    __tablename__ = "sumo_state_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    intersection_id: Mapped[str] = mapped_column(String)
    sim_time_s: Mapped[float] = mapped_column(Float)
    edges: Mapped[dict] = mapped_column(JSON)
    demand_profile: Mapped[str] = mapped_column(String)

class EngineDecision(Base):
    __tablename__ = "engine_decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    intersection_id: Mapped[str] = mapped_column(String)
    phase_durations: Mapped[dict] = mapped_column(JSON)
    priority_mode: Mapped[str] = mapped_column(String)
    vui_score: Mapped[int] = mapped_column(Integer)

class EvEvent(Base):
    __tablename__ = "ev_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ev_id: Mapped[str] = mapped_column(String)
    approach_edge: Mapped[str] = mapped_column(String)
    distance_to_stopline_m: Mapped[float] = mapped_column(Float)
    velocity_kmh: Mapped[float] = mapped_column(Float)
    tti_seconds: Mapped[float] = mapped_column(Float)
    priority_rank: Mapped[str] = mapped_column(String)
