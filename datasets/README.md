# Construction Robots Dataset

This folder contains a synthetic operations dataset for construction robotics.

## File
- `construction_robots_1k.csv`: 1,000 labeled operation records.

## Schema (high-level)
- Context: `site_type`, `terrain`, `weather`, `shift`
- Robot/task: `robot_type`, `task_type`, `autonomy_level`
- Telemetry: `battery_pct`, `payload_kg`, `distance_m`, `task_duration_min`, `cycle_time_sec`, `energy_used_kwh`
- Safety/maintenance: `operator_interventions`, `near_miss_count`, `maintenance_flag`
- Output labels: `productivity_score` (regression), `task_success_label` (binary)

## Regeneration
Use:

```bash
python3 scripts/generate_construction_robot_dataset.py --rows 1000 --output datasets/construction_robots_1k.csv
```

You can choose any row count from 1,000 to 10,000.
