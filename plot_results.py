#!/usr/bin/env python3
"""Generate plots from Task 1/2/3 CSV results.

Reads CSVs from results/ folder and generates three PNG plots:
- task1.png: delay vs window size N
- task2.png: delay vs MSS
- task3.png: delay vs loss probability p
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: matplotlib not installed. Run: pip install matplotlib")
    exit(1)


def read_csv(csv_path: Path) -> Tuple[List[str], List[float]]:
    """Read CSV and return (x_values, y_values)."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    x_values = []
    y_values = []

    with csv_path.open("r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get first column (key)
            key = list(row.keys())[0]
            x_values.append(row[key])
            # Get delay (second column)
            y_values.append(float(row["average_delay_seconds"]))

    return x_values, y_values


def plot_task1(output_dir: Path) -> None:
    """Plot Task 1: delay vs window size N."""
    csv_path = output_dir / "task1_window_size.csv"
    x_values, y_values = read_csv(csv_path)

    # Convert x to integers for cleaner plotting
    x_int = [int(x) for x in x_values]

    plt.figure(figsize=(10, 6))
    plt.plot(x_int, y_values, marker="o", linewidth=2, markersize=8, color="blue")
    plt.xlabel("Window Size (N)", fontsize=12)
    plt.ylabel("Average Transfer Delay (seconds)", fontsize=12)
    plt.title("Task 1: Effect of Window Size on Transfer Delay (MSS=500, p=0.05)", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xscale("log")
    plt.tight_layout()
    plt.savefig(output_dir / "task1.png", dpi=150)
    print(f"Saved: {output_dir / 'task1.png'}")
    plt.close()


def plot_task2(output_dir: Path) -> None:
    """Plot Task 2: delay vs MSS."""
    csv_path = output_dir / "task2_mss.csv"
    x_values, y_values = read_csv(csv_path)

    # Convert x to integers
    x_int = [int(x) for x in x_values]

    plt.figure(figsize=(10, 6))
    plt.plot(x_int, y_values, marker="s", linewidth=2, markersize=8, color="green")
    plt.xlabel("Maximum Segment Size (MSS) in bytes", fontsize=12)
    plt.ylabel("Average Transfer Delay (seconds)", fontsize=12)
    plt.title("Task 2: Effect of MSS on Transfer Delay (N=64, p=0.05)", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "task2.png", dpi=150)
    print(f"Saved: {output_dir / 'task2.png'}")
    plt.close()


def plot_task3(output_dir: Path) -> None:
    """Plot Task 3: delay vs loss probability."""
    csv_path = output_dir / "task3_loss_probability.csv"
    x_values, y_values = read_csv(csv_path)

    # Convert x to floats
    x_float = [float(x) for x in x_values]

    plt.figure(figsize=(10, 6))
    plt.plot(x_float, y_values, marker="^", linewidth=2, markersize=8, color="red")
    plt.xlabel("Packet Loss Probability (p)", fontsize=12)
    plt.ylabel("Average Transfer Delay (seconds)", fontsize=12)
    plt.title("Task 3: Effect of Packet Loss Probability on Transfer Delay (N=64, MSS=500)", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "task3.png", dpi=150)
    print(f"Saved: {output_dir / 'task3.png'}")
    plt.close()


def main() -> None:
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    print("Generating plots from CSV results...")

    try:
        plot_task1(output_dir)
    except FileNotFoundError as e:
        print(f"Skipping Task 1: {e}")

    try:
        plot_task2(output_dir)
    except FileNotFoundError as e:
        print(f"Skipping Task 2: {e}")

    try:
        plot_task3(output_dir)
    except FileNotFoundError as e:
        print(f"Skipping Task 3: {e}")

    print("\nPlot generation complete. Check results/ folder for PNG files.")


if __name__ == "__main__":
    main()
