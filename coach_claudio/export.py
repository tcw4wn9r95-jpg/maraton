"""Export Coach Claudio workout library to TrainingPeaks-compatible .fit files.

Usage:
    python -m coach_claudio.export [--output-dir OUTPUT] [--level LEVEL] [--category CATEGORY]

Generates one .fit workout file per workout template, organized into
folders by level and category. Import these directly into TrainingPeaks
via Settings > Workout Library > Import.
"""

import argparse
import os
import re

from coach_claudio.fit_encoder import FitEncoder
from coach_claudio.workouts import build_library, LEVELS, get_categories


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s\-]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name


def export_workout(workout: dict, output_dir: str) -> str:
    encoder = FitEncoder()
    encoder.add_file_id()

    steps = workout["steps"]
    encoder.add_workout(workout["name"], len(steps))

    for i, s in enumerate(steps):
        encoder.add_workout_step(
            message_index=i,
            duration_type=s["duration_type"],
            duration_value=s["duration_value"],
            target_type=s["target_type"],
            target_value=s["target_value"],
            target_low=s["target_low"],
            target_high=s["target_high"],
            intensity=s["intensity"],
            notes=s.get("notes", ""),
        )

    fit_data = encoder.build()

    level_dir = os.path.join(output_dir, workout["level"], workout["category"])
    os.makedirs(level_dir, exist_ok=True)

    filename = sanitize_filename(workout["name"]) + ".fit"
    filepath = os.path.join(level_dir, filename)

    with open(filepath, "wb") as f:
        f.write(fit_data)

    return filepath


def export_library(output_dir: str = "output",
                   level: str | None = None,
                   category: str | None = None) -> list[str]:
    library = build_library()

    if level:
        library = [w for w in library if w["level"] == level]
    if category:
        library = [w for w in library if w["category"] == category]

    paths = []
    for workout in library:
        path = export_workout(workout, output_dir)
        paths.append(path)

    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Export Coach Claudio workout library to .fit files"
    )
    parser.add_argument(
        "--output-dir", "-o", default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--level", "-l", choices=LEVELS,
        help="Export only this level"
    )
    parser.add_argument(
        "--category", "-c",
        help="Export only this category"
    )
    parser.add_argument(
        "--list-categories", action="store_true",
        help="List available workout categories and exit"
    )

    args = parser.parse_args()

    if args.list_categories:
        print("Available categories:")
        for cat in get_categories():
            print(f"  {cat}")
        return

    paths = export_library(args.output_dir, args.level, args.category)
    print(f"Exported {len(paths)} workout files to {args.output_dir}/")

    by_level = {}
    for p in paths:
        parts = p.split(os.sep)
        lvl = parts[-3] if len(parts) >= 3 else "unknown"
        by_level.setdefault(lvl, 0)
        by_level[lvl] += 1

    for lvl, count in sorted(by_level.items()):
        print(f"  {lvl}: {count} workouts")


if __name__ == "__main__":
    main()
