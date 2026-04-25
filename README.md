# Simple-FTP over UDP (Go-Back-N)

This project implements reliable file transfer over UDP using Go-Back-N ARQ.

## Files

- `Simple_ftp_server.py`: receiver/server
- `Simple_ftp_client.py`: sender/client
- `simple_ftp_common.py`: packet format and checksum helpers
- `compare_files.py`: byte-level transfer validation tool
- `run_experiments.py`: automation for Tasks 1-3 (CSV output)

## Packet Formats

Data packet (header + payload):

- 32-bit sequence number
- 16-bit checksum over payload (UDP-style one's complement checksum)
- 16-bit type = `0x5555`

ACK packet (header only, no payload):

- 32-bit ACKed sequence number
- 16-bit field = `0x0000`
- 16-bit type = `0xAAAA`

## Run Server

Unix-like:

```bash
./Simple_ftp_server 7735 output.txt 0.05
```

Windows:

```powershell
.\Simple_ftp_server.bat 7735 output.txt 0.05
```

Arguments:

- `port` (e.g., 7735)
- `file-name` (output file)
- `p` packet loss probability in `(0, 1)`

Server output on probabilistic drop:

```text
Packet loss, sequence number = X
```

By default, the server only prints required assignment output lines.

## Run Client

Unix-like:

```bash
./Simple_ftp_client serverHost 7735 input.txt 64 500
```

Windows:

```powershell
.\Simple_ftp_client.bat serverHost 7735 input.txt 64 500
```

Arguments:

- `server-host-name`
- `server-port`
- `file-name` (input file)
- `N` window size
- `MSS` maximum segment size in bytes

Optional argument:

- `--timeout` timeout seconds (default `0.5`)

Client output on timeout:

```text
Timeout, sequence number = Y
```

By default, the client only prints required assignment output lines plus final transfer delay.
For extra demo/screenshot logs, add `--verbose` to client/server commands.

## Capture Logs For Demo Screenshots

Server terminal (captures startup, packet-loss, and summary events):

```powershell
.\Simple_ftp_server.bat 7735 output.txt 0.05 --verbose | Tee-Object -FilePath server_demo.log
```

Client terminal (captures send/ACK milestones, timeouts, and summary):

```powershell
.\Simple_ftp_client.bat 127.0.0.1 7735 input.txt 64 500 --verbose | Tee-Object -FilePath client_demo.log
```

These are good moments to screenshot:

- `[SERVER] Listening on UDP port ...`
- `Packet loss, sequence number = X`
- `[CLIENT] Starting transfer: ...`
- `Timeout, sequence number = Y`
- `[SERVER] Ignored out-of-sequence packet ...`
- `[CLIENT] Summary: ...`
- `[SERVER] Summary: ...`

## Verify Output File

```bash
python compare_files.py input.txt output.txt
```

Prints `MATCH` if transfer is correct.

## Experiment Automation (Tasks 1-3)

```bash
python run_experiments.py --input-file input.txt --task all
```

This creates:

- `results/task1_window_size.csv`
- `results/task2_mss.csv`
- `results/task3_loss_probability.csv`

Use these CSV files to generate plots for your report.

## Notes

- All key parameters are runtime-tunable (no hardcoded `N`, `MSS`, or `p`).
- The client appends one zero-length data segment as an EOF marker so the server can terminate cleanly after one transfer.
