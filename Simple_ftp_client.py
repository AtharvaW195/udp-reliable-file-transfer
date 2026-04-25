#!/usr/bin/env python3
"""Simple-FTP client (sender) implementing Go-Back-N over UDP.

Usage:
    Simple_ftp_client.py server-host-name server-port file-name N MSS
"""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import List, Optional

from simple_ftp_common import ACK_TYPE, make_data_packet, parse_packet


DEFAULT_TIMEOUT_SECONDS = 0.5
SOCKET_POLL_SECONDS = 0.02


def _log_key_sequence(sequence_number: int) -> bool:
    return sequence_number < 5 or sequence_number % 100 == 0


def build_segments(file_path: Path, mss: int) -> List[bytes]:
    data = file_path.read_bytes()
    segments = [data[i : i + mss] for i in range(0, len(data), mss)]
    # Always append an explicit empty data segment as EOF marker.
    segments.append(b"")
    return segments


def transfer_file(
    server_host: str,
    server_port: int,
    file_path: Path,
    window_size: int,
    mss: int,
    timeout_seconds: float,
    verbose: bool,
) -> float:
    segments = build_segments(file_path, mss)
    total_segments = len(segments)
    sent_packets = 0
    retransmitted_packets = 0
    ack_packets = 0
    timeout_events = 0

    base = 0
    next_seq = 0
    timer_start: Optional[float] = None

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(SOCKET_POLL_SECONDS)
        server_address = (server_host, server_port)
        if verbose:
            print(
                "[CLIENT] Starting transfer: "
                f"server={server_host}:{server_port}, file={file_path}, N={window_size}, MSS={mss}, "
                f"total_segments={total_segments}",
                flush=True,
            )

        start_time = time.perf_counter()

        while base < total_segments:
            while next_seq < base + window_size and next_seq < total_segments:
                packet = make_data_packet(next_seq, segments[next_seq])
                sock.sendto(packet, server_address)
                sent_packets += 1
                if verbose and _log_key_sequence(next_seq):
                    print(f"[CLIENT] Sent data seq={next_seq}", flush=True)
                if base == next_seq:
                    timer_start = time.perf_counter()
                next_seq += 1

            try:
                response, _ = sock.recvfrom(2048)
                ack_seq, ack_zero_field, packet_type, _ = parse_packet(response)

                if packet_type != ACK_TYPE or ack_zero_field != 0:
                    continue

                if ack_seq < base or ack_seq >= total_segments:
                    continue

                ack_packets += 1
                if verbose and _log_key_sequence(ack_seq):
                    print(f"[CLIENT] Received ACK seq={ack_seq}", flush=True)
                base = ack_seq + 1
                if base == next_seq:
                    timer_start = None
                else:
                    timer_start = time.perf_counter()

            except socket.timeout:
                pass

            if timer_start is not None:
                elapsed = time.perf_counter() - timer_start
                if elapsed >= timeout_seconds:
                    print(f"Timeout, sequence number = {base}")
                    timeout_events += 1
                    for seq in range(base, next_seq):
                        packet = make_data_packet(seq, segments[seq])
                        sock.sendto(packet, server_address)
                        retransmitted_packets += 1
                    timer_start = time.perf_counter()

        end_time = time.perf_counter()
        if verbose:
            print(
                "[CLIENT] Summary: "
                f"sent_packets={sent_packets}, ack_packets={ack_packets}, "
                f"retransmitted_packets={retransmitted_packets}, timeout_events={timeout_events}",
                flush=True,
            )
        return end_time - start_time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple-FTP client using Go-Back-N")
    parser.add_argument("server_host", help="Server host name or IP")
    parser.add_argument("server_port", type=int, help="Server UDP port")
    parser.add_argument("file_name", help="Input file to transfer")
    parser.add_argument("window_size", type=int, help="Go-Back-N window size N")
    parser.add_argument("mss", type=int, help="Maximum Segment Size")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable extra logs for debugging/demo screenshots",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.server_port <= 0 or args.server_port > 65535:
        raise ValueError("server_port must be in [1, 65535]")
    if args.window_size <= 0:
        raise ValueError("window_size must be positive")
    if args.mss <= 0:
        raise ValueError("mss must be positive")
    if args.timeout <= 0:
        raise ValueError("timeout must be positive")

    input_path = Path(args.file_name)
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    delay_seconds = transfer_file(
        server_host=args.server_host,
        server_port=args.server_port,
        file_path=input_path,
        window_size=args.window_size,
        mss=args.mss,
        timeout_seconds=args.timeout,
        verbose=args.verbose,
    )
    print(f"Transfer complete. Delay = {delay_seconds:.6f} seconds")


if __name__ == "__main__":
    main()
