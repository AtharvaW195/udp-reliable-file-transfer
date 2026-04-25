#!/usr/bin/env python3
"""Automate Tasks 1-3 experiment runs for Simple-FTP.

This script launches server/client subprocesses repeatedly and writes CSV outputs.
Run server and client hosts as needed; for cross-host runs, you can still use this script
on one side by adapting command templates.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import time
from pathlib import Path
from statistics import mean
from typing import Iterable, List


def run_client(
    python_cmd: str,
    server_host: str,
    server_port: int,
    input_file: str,
    window_size: int,
    mss: int,
    timeout: float,
) -> float:
    cmd = [
        python_cmd,
        "Simple_ftp_client.py",
        server_host,
        str(server_port),
        input_file,
        str(window_size),
        str(mss),
        "--timeout",
        str(timeout),
    ]
    start = time.perf_counter()
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    end = time.perf_counter()

    for line in completed.stdout.splitlines():
        if line.startswith("Transfer complete. Delay ="):
            try:
                value = float(line.split("=")[1].split()[0])
                return value
            except (ValueError, IndexError):
                break
    return end - start


def run_server(
    python_cmd: str,
    port: int,
    output_file: str,
    p: float,
):
    cmd = [python_cmd, "Simple_ftp_server.py", str(port), output_file, str(p)]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_trials(
    python_cmd: str,
    server_host: str,
    server_port: int,
    input_file: str,
    output_file: str,
    window_size: int,
    mss: int,
    p: float,
    timeout: float,
    trials: int,
) -> List[float]:
    delays: List[float] = []
    for _ in range(trials):
        server_proc = run_server(python_cmd, server_port, output_file, p)
        time.sleep(0.2)
        try:
            delay = run_client(
                python_cmd,
                server_host,
                server_port,
                input_file,
                window_size,
                mss,
                timeout,
            )
            delays.append(delay)
        finally:
            server_proc.wait(timeout=10)
    return delays


def write_csv(path: Path, rows: Iterable[dict], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="ascii") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def task1_values() -> List[int]:
    return [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]


def task2_values() -> List[int]:
    return list(range(100, 1001, 100))


def task3_values() -> List[float]:
    return [round(x / 100.0, 2) for x in range(1, 11)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Simple-FTP experiments")
    parser.add_argument("--python", default="python", help="Python command")
    parser.add_argument("--server-host", default="127.0.0.1")
    parser.add_argument("--server-port", type=int, default=7735)
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--output-file", default="received_output.bin")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument(
        "--task",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which task sweep to run",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    if args.task in ("1", "all"):
        rows = []
        for n in task1_values():
            delays = run_trials(
                python_cmd=args.python,
                server_host=args.server_host,
                server_port=args.server_port,
                input_file=args.input_file,
                output_file=args.output_file,
                window_size=n,
                mss=500,
                p=0.05,
                timeout=args.timeout,
                trials=args.trials,
            )
            rows.append({"N": n, "average_delay_seconds": f"{mean(delays):.6f}"})
            print(f"Task1 N={n}: avg delay={mean(delays):.6f}")
        write_csv(output_dir / "task1_window_size.csv", rows, ["N", "average_delay_seconds"])

    if args.task in ("2", "all"):
        rows = []
        for mss in task2_values():
            delays = run_trials(
                python_cmd=args.python,
                server_host=args.server_host,
                server_port=args.server_port,
                input_file=args.input_file,
                output_file=args.output_file,
                window_size=64,
                mss=mss,
                p=0.05,
                timeout=args.timeout,
                trials=args.trials,
            )
            rows.append({"MSS": mss, "average_delay_seconds": f"{mean(delays):.6f}"})
            print(f"Task2 MSS={mss}: avg delay={mean(delays):.6f}")
        write_csv(output_dir / "task2_mss.csv", rows, ["MSS", "average_delay_seconds"])

    if args.task in ("3", "all"):
        rows = []
        for p in task3_values():
            delays = run_trials(
                python_cmd=args.python,
                server_host=args.server_host,
                server_port=args.server_port,
                input_file=args.input_file,
                output_file=args.output_file,
                window_size=64,
                mss=500,
                p=p,
                timeout=args.timeout,
                trials=args.trials,
            )
            rows.append({"p": f"{p:.2f}", "average_delay_seconds": f"{mean(delays):.6f}"})
            print(f"Task3 p={p:.2f}: avg delay={mean(delays):.6f}")
        write_csv(output_dir / "task3_loss_probability.csv", rows, ["p", "average_delay_seconds"])


if __name__ == "__main__":
    main()
