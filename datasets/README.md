# Construction Robots Dataset (Industry-Ready)

This dataset is structured for **high-value construction programs** (data centers, semiconductor fabs, hospitals, airport terminals, tunnels, and long-span bridges).

## File
- `construction_robots_1k.csv`: 1,000 operations records with productivity and task-success labels.

## Why this version is industry-ready
- Uses scenario profiles for high-value project classes (`asset_class`, `program_value_band`, `schedule_criticality`).
- Includes quality-control fields (`qa_tolerance_mm`, `qa_deviation_mm`, `qa_pass_flag`).
- Includes risk/commercial fields (`value_at_risk_musd`, `delay_risk_pct`, `estimated_rework_cost_usd`).
- Uses weighted operating conditions and robot-specific envelopes (payload, cycle time, energy rate) to avoid purely uniform random data.

## Columns (grouped)
- Program context: `asset_class`, `program_value_band`, `schedule_criticality`
- Robot operation: `robot_type`, `task_type`, `autonomy_level`, `payload_kg`, `task_duration_min`, `cycle_time_sec`
- Site conditions: `shift`, `terrain`, `weather`, `battery_pct`, `signal_strength_pct`
- Safety/maintenance: `operator_interventions`, `near_miss_count`, `planned_maintenance_flag`, `unplanned_downtime_min`
- Quality/risk: `qa_tolerance_mm`, `qa_deviation_mm`, `qa_pass_flag`, `value_at_risk_musd`, `delay_risk_pct`, `estimated_rework_cost_usd`
- Targets: `productivity_score` (regression), `task_success_label` (binary)

## Regenerate
```bash
python3 scripts/generate_construction_robot_dataset.py --rows 1000 --output datasets/construction_robots_1k.csv
```

Valid row range: **1,000 to 10,000**.
