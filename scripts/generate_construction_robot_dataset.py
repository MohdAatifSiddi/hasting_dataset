#!/usr/bin/env python3
"""Generate an industry-ready construction robotics dataset (1k-10k rows).

The generator uses domain profiles for high-value construction programs
(e.g., data centers, semiconductor fabs, hospitals, airports, bridges)
and scenario-based operating envelopes rather than fully random sampling.
"""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class ProgramProfile:
    asset_class: str
    value_band: str
    value_at_risk_range_musd: tuple[float, float]
    schedule_criticality: str
    qa_tolerance_mm: tuple[float, float]


PROGRAMS: tuple[ProgramProfile, ...] = (
    ProgramProfile("data_center", "high", (1.5, 8.0), "critical", (2.0, 5.0)),
    ProgramProfile("semiconductor_fab", "very_high", (3.0, 12.0), "critical", (1.0, 3.0)),
    ProgramProfile("hospital", "high", (1.0, 6.5), "critical", (2.0, 4.0)),
    ProgramProfile("airport_terminal", "high", (1.2, 7.0), "high", (3.0, 6.0)),
    ProgramProfile("metro_tunnel", "very_high", (2.0, 9.5), "high", (4.0, 10.0)),
    ProgramProfile("long_span_bridge", "very_high", (2.5, 11.0), "critical", (3.0, 8.0)),
)

ROBOT_LIBRARY: dict[str, dict[str, object]] = {
    "autonomous_excavator": {
        "tasks": ("bulk_excavation", "precision_grading"),
        "payload_range_kg": (800, 4000),
        "cycle_time_sec": (95, 420),
        "energy_kwh_h": (18.0, 44.0),
    },
    "rebar_tying_robot": {
        "tasks": ("rebar_tying",),
        "payload_range_kg": (15, 160),
        "cycle_time_sec": (6, 32),
        "energy_kwh_h": (1.5, 4.6),
    },
    "bricklaying_robot": {
        "tasks": ("masonry",),
        "payload_range_kg": (80, 500),
        "cycle_time_sec": (7, 42),
        "energy_kwh_h": (2.0, 7.2),
    },
    "concrete_printing_robot": {
        "tasks": ("concrete_printing",),
        "payload_range_kg": (100, 700),
        "cycle_time_sec": (35, 180),
        "energy_kwh_h": (6.5, 18.0),
    },
    "inspection_drone": {
        "tasks": ("qa_inspection", "progress_scan"),
        "payload_range_kg": (1, 25),
        "cycle_time_sec": (15, 140),
        "energy_kwh_h": (0.3, 2.4),
    },
    "material_transport_rover": {
        "tasks": ("material_transport",),
        "payload_range_kg": (250, 2600),
        "cycle_time_sec": (60, 360),
        "energy_kwh_h": (4.5, 16.0),
    },
}

WEATHER_IMPACT = {
    "clear": 0,
    "cloudy": -1,
    "windy": -4,
    "light_rain": -6,
    "heavy_rain": -12,
    "high_heat": -5,
    "cold": -4,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def weighted_weather() -> str:
    options = ["clear", "cloudy", "windy", "light_rain", "heavy_rain", "high_heat", "cold"]
    weights = [0.42, 0.15, 0.12, 0.12, 0.05, 0.08, 0.06]
    return random.choices(options, weights=weights, k=1)[0]


def weighted_program() -> ProgramProfile:
    weights = [0.24, 0.16, 0.20, 0.14, 0.13, 0.13]
    return random.choices(PROGRAMS, weights=weights, k=1)[0]


def record(i: int, t0: datetime) -> dict[str, object]:
    program = weighted_program()
    robot = random.choice(tuple(ROBOT_LIBRARY.keys()))
    robot_spec = ROBOT_LIBRARY[robot]
    task = random.choice(robot_spec["tasks"])

    weather = weighted_weather()
    shift = random.choices(["day", "night"], weights=[0.73, 0.27], k=1)[0]
    terrain = random.choices(["flat", "mixed", "sloped", "confined"], [0.44, 0.32, 0.12, 0.12], k=1)[0]

    autonomy_level = random.choices([2, 3, 4, 5], weights=[0.16, 0.34, 0.31, 0.19], k=1)[0]
    battery_pct = random.randint(18, 100)
    signal_strength_pct = random.randint(70, 100)
    operator_interventions = max(0, int(round(random.gauss(2.4, 1.5))))

    payload_kg = random.randint(*robot_spec["payload_range_kg"])
    duration_min = random.randint(20, 360)
    cycle_time_sec = round(random.uniform(*robot_spec["cycle_time_sec"]), 2)
    energy_rate = random.uniform(*robot_spec["energy_kwh_h"])
    energy_used_kwh = round(duration_min / 60 * energy_rate, 2)

    qa_tol_mm = round(random.uniform(*program.qa_tolerance_mm), 2)
    achieved_mm = round(qa_tol_mm * random.uniform(0.55, 1.25), 2)
    qa_pass = int(achieved_mm <= qa_tol_mm)

    near_miss_count = 1 if random.random() < 0.035 else 0
    planned_maint = 1 if random.random() < 0.11 else 0
    unplanned_downtime_min = int(max(0, random.gauss(8, 14))) if planned_maint else int(max(0, random.gauss(3, 7)))

    value_at_risk_musd = round(random.uniform(*program.value_at_risk_range_musd), 2)
    baseline_prod = 79 + autonomy_level * 3.2 - operator_interventions * 2.3 + WEATHER_IMPACT[weather]
    baseline_prod += -5 if shift == "night" else 0
    baseline_prod += -4 if terrain in {"sloped", "confined"} else 0
    baseline_prod += -7 if battery_pct < 30 else 0
    baseline_prod += 2 if signal_strength_pct > 92 else 0
    productivity_score = round(clamp(baseline_prod + random.uniform(-4.5, 4.5), 35, 99), 2)

    delay_risk_pct = round(clamp(100 - productivity_score + unplanned_downtime_min * 0.35 + near_miss_count * 10, 1, 95), 2)
    estimated_rework_cost_usd = round(max(0.0, value_at_risk_musd * 1_000_000 * (1 - qa_pass) * random.uniform(0.002, 0.017)), 2)

    task_success_label = int(productivity_score >= 72 and near_miss_count == 0 and qa_pass == 1)

    return {
        "record_id": f"CRI-{i:06}",
        "event_time_utc": (t0 + timedelta(minutes=i * 9)).isoformat(timespec="seconds") + "Z",
        "asset_class": program.asset_class,
        "program_value_band": program.value_band,
        "schedule_criticality": program.schedule_criticality,
        "robot_type": robot,
        "task_type": task,
        "shift": shift,
        "terrain": terrain,
        "weather": weather,
        "autonomy_level": autonomy_level,
        "battery_pct": battery_pct,
        "signal_strength_pct": signal_strength_pct,
        "payload_kg": payload_kg,
        "task_duration_min": duration_min,
        "cycle_time_sec": cycle_time_sec,
        "energy_used_kwh": energy_used_kwh,
        "operator_interventions": operator_interventions,
        "near_miss_count": near_miss_count,
        "planned_maintenance_flag": planned_maint,
        "unplanned_downtime_min": unplanned_downtime_min,
        "qa_tolerance_mm": qa_tol_mm,
        "qa_deviation_mm": achieved_mm,
        "qa_pass_flag": qa_pass,
        "value_at_risk_musd": value_at_risk_musd,
        "delay_risk_pct": delay_risk_pct,
        "estimated_rework_cost_usd": estimated_rework_cost_usd,
        "productivity_score": productivity_score,
        "task_success_label": task_success_label,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate industry-ready construction robot dataset")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows (1000-10000)")
    parser.add_argument("--output", type=str, default="datasets/construction_robots_1k.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    if not (1000 <= args.rows <= 10000):
        raise SystemExit("--rows must be between 1000 and 10000")

    random.seed(args.seed)
    t0 = datetime(2025, 1, 1, 6, 0, 0)
    rows = [record(i + 1, t0) for i in range(args.rows)]

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {args.rows} rows at {args.output}")


if __name__ == "__main__":
    main()
