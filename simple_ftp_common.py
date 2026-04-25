"""Shared packet helpers for Simple-FTP over UDP using Go-Back-N."""

from __future__ import annotations

import struct
from typing import Tuple

# 32-bit sequence number, 16-bit checksum/zero, 16-bit packet type
HEADER_FORMAT = "!IHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

DATA_TYPE = 0x5555
ACK_TYPE = 0xAAAA


def compute_udp_style_checksum(data: bytes) -> int:
    """Compute 16-bit one's complement checksum over payload bytes."""
    if len(data) % 2 == 1:
        data += b"\x00"

    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    checksum = ~checksum & 0xFFFF
    return checksum


def make_data_packet(sequence_number: int, payload: bytes) -> bytes:
    checksum = compute_udp_style_checksum(payload)
    header = struct.pack(HEADER_FORMAT, sequence_number, checksum, DATA_TYPE)
    return header + payload


def make_ack_packet(sequence_number: int) -> bytes:
    return struct.pack(HEADER_FORMAT, sequence_number, 0, ACK_TYPE)


def parse_packet(packet: bytes) -> Tuple[int, int, int, bytes]:
    """Return (sequence_number, checksum_or_zero, packet_type, payload)."""
    if len(packet) < HEADER_SIZE:
        raise ValueError("Packet too short")
    sequence_number, checksum_or_zero, packet_type = struct.unpack(
        HEADER_FORMAT, packet[:HEADER_SIZE]
    )
    payload = packet[HEADER_SIZE:]
    return sequence_number, checksum_or_zero, packet_type, payload
