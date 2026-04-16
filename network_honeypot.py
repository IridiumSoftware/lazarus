"""
network_honeypot.py — Network Honeypot
══════════════════════════════════════

Listens on commonly-scanned ports and serves a text file to anything
that connects. Looks like an easy target. Anything that takes the
bait gets a message instead.

Ports:
  8080  — HTTP (fake web admin panel)
  2222  — SSH (fake SSH banner)
  21    — FTP (fake FTP banner)
  3306  — MySQL (fake database)
  8443  — HTTPS alt (fake management console)

Run: python3 network_honeypot.py
Run background: nohup python3 network_honeypot.py &

Requires: sudo for ports < 1024 (21)
Without sudo: only ports >= 1024 will bind (8080, 2222, 8443, 3306)
"""

import socket
import threading
import os
import sys
import json
from datetime import datetime

# File served to anyone who connects.
# Create a HONEYPOT_BANNER.txt in the same directory, or it falls back
# to a default message.
BANNER_PATH = os.path.join(os.path.dirname(__file__), "HONEYPOT_BANNER.txt")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

DEFAULT_BANNER = """
==========================================================
  You have reached a monitored honeypot.
  This connection has been logged.
  Have a nice day.
==========================================================
"""

if os.path.exists(BANNER_PATH):
    with open(BANNER_PATH, "r") as f:
        BANNER_CONTENT = f.read()
else:
    BANNER_CONTENT = DEFAULT_BANNER


def log_connection(port, remote_addr, service):
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(LOG_DIR, f"honeypot_{today}.jsonl")

    entry = {
        "timestamp": datetime.now().isoformat(),
        "remote": remote_addr,
        "port": port,
        "service": service,
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {service}:{port} <- {remote_addr}")


def serve_http(conn, addr, port):
    try:
        conn.settimeout(5)
        conn.recv(4096)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            f"Content-Length: {len(BANNER_CONTENT)}\r\n"
            "Server: Apache/2.4.41\r\n"
            "\r\n"
            f"{BANNER_CONTENT}"
        )
        conn.sendall(response.encode())
        log_connection(port, f"{addr[0]}:{addr[1]}", "HTTP")
    except Exception:
        pass
    finally:
        conn.close()


def serve_ssh(conn, addr, port):
    try:
        conn.settimeout(5)
        banner = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"
        conn.sendall(banner.encode())
        conn.recv(4096)
        conn.sendall(BANNER_CONTENT.encode())
        log_connection(port, f"{addr[0]}:{addr[1]}", "SSH")
    except Exception:
        pass
    finally:
        conn.close()


def serve_ftp(conn, addr, port):
    try:
        conn.settimeout(5)
        conn.sendall(b"220 Welcome to FTP service\r\n")
        conn.recv(4096)
        conn.sendall(b"331 Password required\r\n")
        conn.recv(4096)
        conn.sendall(b"230 Login successful\r\n")
        conn.recv(4096)
        conn.sendall(BANNER_CONTENT.encode())
        log_connection(port, f"{addr[0]}:{addr[1]}", "FTP")
    except Exception:
        pass
    finally:
        conn.close()


def serve_mysql(conn, addr, port):
    try:
        conn.settimeout(5)
        greeting = b"\x00\x00\x00\x0a5.7.42\x00"
        conn.sendall(greeting)
        conn.recv(4096)
        conn.sendall(BANNER_CONTENT.encode())
        log_connection(port, f"{addr[0]}:{addr[1]}", "MySQL")
    except Exception:
        pass
    finally:
        conn.close()


SERVICES = {
    8080: ("HTTP-Admin", serve_http),
    2222: ("SSH", serve_ssh),
    21:   ("FTP", serve_ftp),
    3306: ("MySQL", serve_mysql),
    8443: ("HTTPS-Mgmt", serve_http),
}


def listen_on_port(port, name, handler):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        print(f"  + {name} listening on :{port}")

        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handler, args=(conn, addr, port), daemon=True)
            t.start()
    except PermissionError:
        print(f"  - {name}:{port} — needs sudo (skipped)")
    except OSError as e:
        print(f"  - {name}:{port} — {e}")


def main():
    print("=" * 55)
    print("  Network Honeypot")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)

    threads = []
    for port, (name, handler) in SERVICES.items():
        t = threading.Thread(target=listen_on_port, args=(port, name, handler), daemon=True)
        t.start()
        threads.append(t)

    print("=" * 55)
    print("  Waiting for connections... (Ctrl+C to stop)")
    print("=" * 55)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n  Stopped. Logs in ./logs/")


if __name__ == "__main__":
    main()
