#!/usr/bin/env python3
"""Simple-FTP server (receiver) implementing Go-Back-N over UDP.

Usage:
    Simple_ftp_server.py port file-name p
"""

from __future__ import annotations

import argparse
import random
import socket
from pathlib import Path

from simple_ftp_common import (
    DATA_TYPE,
    compute_udp_style_checksum,
    make_ack_packet,
    parse_packet,
)


def _log_key_sequence(sequence_number: int) -> bool:
    return sequence_number < 5 or sequence_number % 100 == 0


def run_server(port: int, output_path: Path, loss_probability: float, verbose: bool) -> None:
    expected_seq = 0
    received_packets = 0
    accepted_packets = 0
    ignored_out_of_sequence = 0
    ignored_bad_checksum = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", port))
        if verbose:
            print(
                f"[SERVER] Listening on UDP port {port}; output={output_path}; loss_probability={loss_probability}",
                flush=True,
            )

        with output_path.open("wb") as output_file:
            while True:
                packet, client_address = sock.recvfrom(65535)
                received_packets += 1

                try:
                    sequence_number, recv_checksum, packet_type, payload = parse_packet(packet)
                except ValueError:
                    continue

                if packet_type != DATA_TYPE:
                    continue

                if random.random() <= loss_probability:
                    print(f"Packet loss, sequence number = {sequence_number}")
                    continue

                expected_checksum = compute_udp_style_checksum(payload)
                checksum_ok = recv_checksum == expected_checksum

                if checksum_ok and sequence_number == expected_seq:
                    if len(payload) == 0:
                        ack_packet = make_ack_packet(sequence_number)
                        sock.sendto(ack_packet, client_address)
                        if verbose:
                            print(
                                "[SERVER] EOF marker received; "
                                f"seq={sequence_number}, sent ACK, transfer complete",
                                flush=True,
                            )
                            print(
                                "[SERVER] Summary: "
                                f"received_packets={received_packets}, "
                                f"accepted_packets={accepted_packets}, "
                                f"ignored_out_of_sequence={ignored_out_of_sequence}, "
                                f"ignored_bad_checksum={ignored_bad_checksum}",
                                flush=True,
                            )
                        break

                    output_file.write(payload)
                    output_file.flush()
                    ack_packet = make_ack_packet(sequence_number)
                    sock.sendto(ack_packet, client_address)
                    accepted_packets += 1
                    if verbose and _log_key_sequence(sequence_number):
                        print(
                            f"[SERVER] Accepted data seq={sequence_number}, bytes={len(payload)}, sent ACK",
                            flush=True,
                        )
                    expected_seq += 1
                # As required in the project statement, out-of-sequence or bad checksum:
                # do nothing.
                else:
                    if not checksum_ok:
                        ignored_bad_checksum += 1
                        if verbose and _log_key_sequence(sequence_number):
                            print(
                                f"[SERVER] Ignored bad-checksum packet seq={sequence_number}",
                                flush=True,
                            )
                    else:
                        ignored_out_of_sequence += 1
                        if verbose and _log_key_sequence(sequence_number):
                            print(
                                "[SERVER] Ignored out-of-sequence packet "
                                f"seq={sequence_number}, expected={expected_seq}",
                                flush=True,
                            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple-FTP server using Go-Back-N")
    parser.add_argument("port", type=int, help="UDP listening port (e.g., 7735)")
    parser.add_argument("file_name", help="Output file name")
    parser.add_argument("p", type=float, help="Packet loss probability in (0, 1)")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable extra logs for debugging/demo screenshots",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.port <= 0 or args.port > 65535:
        raise ValueError("port must be in [1, 65535]")
    if not (0.0 < args.p < 1.0):
        raise ValueError("p must be in (0, 1)")

    output_path = Path(args.file_name)
    run_server(args.port, output_path, args.p, args.verbose)


if __name__ == "__main__":
    main()
