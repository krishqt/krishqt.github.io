# Smart Port Scanner

A production-ready Python CLI tool to scan a target IP across a port range (1–1000) using multithreading, detect common services (HTTP/SSH/FTP), show colored output, and save results to a file.

## Project Structure

```text
.
├── main.py
├── scanner
│   ├── __init__.py
│   └── port_scanner.py
└── utils
    ├── __init__.py
    ├── colors.py
    └── file_utils.py
```

## Requirements

- Python 3.10+

## How to Run

From the repository root:

```bash
python3 main.py -t 127.0.0.1
```

### Useful Arguments (nmap-like flags)

- `-t, --target` (required): target IP address
- `-p, --ports`: port range in `START-END` format (default: `1-1000`)
- `-T, --threads`: number of threads (default: `200`)
- `--timeout`: socket timeout in seconds (default: `0.7`)
- `-o, --output`: output file path (default: `scan_results.txt`)

### Example

```bash
python3 main.py -t 192.168.1.10 -p 1-1000 -T 300 --timeout 0.5 -o my_scan.txt
```

Results are printed in color in the terminal and saved to the output file.
