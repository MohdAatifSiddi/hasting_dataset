#!/usr/bin/env python3
"""Generate a synthetic construction robot operations dataset (1k-10k rows)."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta

SITE_TYPES = [
    "residential",
    "commercial",
    "infrastructure",
    "industrial",
    "energy",
]
ROBOT_TYPES = [
    "autonomous_excavator",
    "rebar_tying_robot",
    "bricklaying_robot",
    "concrete_printing_robot",
    "inspection_drone",
    "demolition_robot",
    "material_transport_rover",
]
TASKS = [
    "excavation",
    "trenching",
    "masonry",
    "rebar_tying",
    "concrete_printing",
    "site_inspection",
    "debris_removal",
    "material_transport",
]
TERRAINS = ["flat", "rocky", "muddy", "mixed", "sloped"]
WEATHERS = ["clear", "windy", "light_rain", "heavy_rain", "fog", "high_heat", "cold"]
SHIFTS = ["day", "night"]


def productivity_score(base_efficiency: float, battery: int, weather: str, terrain: str) -> float:
    score = base_efficiency
    if battery < 25:
        score -= 15
    elif battery < 40:
        score -= 7

    if weather in {"heavy_rain", "fog"}:
        score -= 10
    elif weather in {"windy", "high_heat", "cold"}:
        score -= 4

    if terrain in {"rocky", "muddy", "sloped"}:
        score -= 6

    return max(0.0, min(100.0, round(score + random.uniform(-6, 6), 2)))


def make_row(i: int, start: datetime) -> dict[str, object]:
    robot = random.choice(ROBOT_TYPES)
    task = random.choice(TASKS)
    site = random.choice(SITE_TYPES)
    terrain = random.choice(TERRAINS)
    weather = random.choice(WEATHERS)
    shift = random.choice(SHIFTS)
    battery = random.randint(10, 100)
    payload = random.randint(0, 4000)
    duration = random.randint(20, 360)
    distance = random.randint(30, 5000)
    autonomy_level = random.randint(2, 5)
    operator_interventions = max(0, int(random.gauss(3, 2)))
    near_miss_count = 1 if random.random() < 0.06 else 0
    maintenance_flag = 1 if random.random() < 0.12 else 0

    base_efficiency = 68 + autonomy_level * 5 - operator_interventions * 2
    productivity = productivity_score(base_efficiency, battery, weather, terrain)
    cycle_time_sec = round(random.uniform(45, 420), 2)
    energy_kwh = round((duration / 60) * random.uniform(2.5, 16.0), 2)

    success = 1
    if productivity < 50 or near_miss_count > 0:
        success = 0

    return {
        "record_id": f"CR-{i:06}",
        "event_time_utc": (start + timedelta(minutes=i * 7)).isoformat(timespec="seconds") + "Z",
        "site_type": site,
        "robot_type": robot,
        "task_type": task,
        "shift": shift,
        "terrain": terrain,
        "weather": weather,
        "autonomy_level": autonomy_level,
        "battery_pct": battery,
        "payload_kg": payload,
        "distance_m": distance,
        "task_duration_min": duration,
        "cycle_time_sec": cycle_time_sec,
        "energy_used_kwh": energy_kwh,
        "operator_interventions": operator_interventions,
        "near_miss_count": near_miss_count,
        "maintenance_flag": maintenance_flag,
        "productivity_score": productivity,
        "task_success_label": success,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic construction robot dataset")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows (1000-10000)")
    parser.add_argument(
        "--output",
        type=str,
        default="datasets/construction_robots_1k.csv",
        help="Output CSV path",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    if not (1000 <= args.rows <= 10000):
        raise SystemExit("--rows must be between 1000 and 10000")

    random.seed(args.seed)
    start = datetime(2025, 1, 1, 0, 0, 0)
    rows = [make_row(i + 1, start) for i in range(args.rows)]

    fieldnames = list(rows[0].keys())
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {args.rows} rows at {args.output}")


if __name__ == "__main__":
    main()
