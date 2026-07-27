import os
import sqlite_utils
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "usage.db",
)


def _get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite_utils.Database(DB_PATH)
    db["usage_log"].create(
        {
            "id": int,
            "api_key": str,
            "model": str,
            "duration_ms": int,
            "input_size_bytes": int,
            "timestamp": str,
            "latency_ms": int,
            "status_code": int,
        },
        pk="id",
        if_not_exists=True,
    )
    _migrate_columns(db)
    return db


def _migrate_columns(db):
    cols = db["usage_log"].columns_dict
    if "latency_ms" not in cols:
        db["usage_log"].add_column("latency_ms", int)
    if "status_code" not in cols:
        db["usage_log"].add_column("status_code", int)


def log_usage(
    api_key: str,
    model: str,
    duration_ms: int,
    input_size_bytes: int,
    latency_ms: int,
    status_code: int,
) -> None:
    db = _get_db()
    db["usage_log"].insert(
        {
            "api_key": api_key,
            "model": model,
            "duration_ms": duration_ms,
            "input_size_bytes": input_size_bytes,
            "timestamp": _now(),
            "latency_ms": latency_ms,
            "status_code": status_code,
        }
    )


def get_usage(api_key: str, days: int = 30) -> dict:
    db = _get_db()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = list(
        db["usage_log"]
        .rows_where("api_key = ? AND timestamp >= ?", (api_key, since))
    )
    total_requests = len(rows)
    total_duration = sum(r["duration_ms"] for r in rows)
    total_input = sum(r["input_size_bytes"] for r in rows)
    avg_duration = total_duration / total_requests if total_requests > 0 else 0
    return {
        "total_requests": total_requests,
        "total_duration_ms": total_duration,
        "total_input_bytes": total_input,
        "avg_duration_ms": avg_duration,
        "period_days": days,
    }


def get_analytics(api_key: str, days: int = 30) -> dict:
    db = _get_db()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = list(
        db["usage_log"]
        .rows_where("api_key = ? AND timestamp >= ?", (api_key, since))
    )
    total_requests = len(rows)
    total_duration = sum(r["duration_ms"] for r in rows)
    total_input = sum(r["input_size_bytes"] for r in rows)
    total_latency = sum(r["latency_ms"] for r in rows)
    avg_duration = total_duration / total_requests if total_requests > 0 else 0
    avg_latency = total_latency / total_requests if total_requests > 0 else 0
    errors = sum(1 for r in rows if r["status_code"] >= 400)
    error_rate = (errors / total_requests * 100) if total_requests > 0 else 0

    per_day = {}
    for r in rows:
        date = r["timestamp"][:10]
        if date not in per_day:
            per_day[date] = {"requests": 0, "errors": 0, "latency_sum": 0}
        per_day[date]["requests"] += 1
        if r["status_code"] >= 400:
            per_day[date]["errors"] += 1
        per_day[date]["latency_sum"] += r["latency_ms"]

    per_day_breakdown = []
    for date in sorted(per_day.keys()):
        d = per_day[date]
        per_day_breakdown.append(
            {
                "date": date,
                "requests": d["requests"],
                "errors": d["errors"],
                "avg_latency_ms": d["latency_sum"] / d["requests"] if d["requests"] > 0 else 0,
            }
        )

    return {
        "total_requests": total_requests,
        "total_duration_ms": total_duration,
        "total_input_bytes": total_input,
        "avg_duration_ms": avg_duration,
        "avg_latency_ms": avg_latency,
        "error_rate": error_rate,
        "period_days": days,
        "per_day_breakdown": per_day_breakdown,
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()