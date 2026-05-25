#!/usr/bin/env python3
import base64, socket, ssl, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, os, time

SOURCE_URLS = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/configs/vless.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/configs/vless_reality.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/sub/vless",
]

OUTPUT_FILE = "configs/working.txt"
OUTPUT_JSON = "configs/stats.json"
TIMEOUT = 5
MAX_WORKERS = 50


def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [WARN] Could not fetch {url}: {e}")
        return ""


def decode_subscription(text):
    text = text.strip()
    try:
        decoded = base64.b64decode(text + "==").decode("utf-8", errors="ignore")
        if decoded.startswith("vless://") or "\nvless://" in decoded:
            return [l.strip() for l in decoded.splitlines() if l.strip()]
    except Exception:
        pass
    return [l.strip() for l in text.splitlines() if l.strip()]


def parse_vless(uri):
    try:
        without_scheme = uri[len("vless://"):]
        at_idx = without_scheme.rfind("@")
        if at_idx == -1:
            return None
        host_part = without_scheme[at_idx + 1:]
        for sep in ("?", "#", "/"):
            idx = host_part.find(sep)
            if idx != -1:
                host_part = host_part[:idx]
        if host_part.startswith("["):
            bracket = host_part.find("]")
            host = host_part[1:bracket]
            port_str = host_part[bracket + 2:]
        elif ":" in host_part:
            parts = host_part.rsplit(":", 1)
            host, port_str = parts[0], parts[1]
        else:
            return None
        return host, int(port_str)
    except Exception:
        return None


def check_tcp(host, port):
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return True
    except Exception:
        return False


def check_tls(host, port):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return True
    except Exception:
        return False


def check_config(uri):
    parsed = parse_vless(uri)
    if parsed is None:
        return uri, False, "parse_error"
    host, port = parsed
    if check_tcp(host, port):
        return uri, True, "tcp_ok"
    if check_tls(host, port):
        return uri, True, "tls_ok"
    return uri, False, "unreachable"


def main():
    print("=== VLESS Config Checker ===\n")

    print("[1/3] Collecting configs...")
    all_configs = set()
    for url in SOURCE_URLS:
        print(f"  Fetching {url} ...")
        raw = fetch_url(url)
        if not raw:
            continue
        lines = decode_subscription(raw)
        vless = [l for l in lines if l.startswith("vless://")]
        print(f"    Found {len(vless)} configs")
        all_configs.update(vless)

    configs = list(all_configs)
    print(f"  Total unique: {len(configs)}\n")

    if not configs:
        print("No configs found. Exiting.")
        sys.exit(0)

    print(f"[2/3] Checking {len(configs)} configs...")
    working, failed, errors = [], 0, 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_config, uri): uri for uri in configs}
        done = 0
        for future in as_completed(futures):
            done += 1
            uri, ok, reason = future.result()
            if ok:
                working.append(uri)
            elif reason == "parse_error":
                errors += 1
            else:
                failed += 1
            if done % 50 == 0 or done == len(configs):
                print(f"  {done}/{len(configs)} | Working: {len(working)}")

    elapsed = round(time.time() - start, 1)
    print(f"\n[3/3] Saving results...")

    os.makedirs("configs", exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(working) + "\n" if working else "")

    if working:
        encoded = base64.b64encode("\n".join(working).encode()).decode()
        with open("configs/working_sub.txt", "w") as f:
            f.write(encoded)

    stats = {
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_checked": len(configs),
        "working": len(working),
        "failed": failed,
        "parse_errors": errors,
        "elapsed_seconds": elapsed,
    }
    with open(OUTPUT_JSON, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"  Saved {len(working)} working configs.")
    print(f"  Stats: {stats}\nDone.")


if __name__ == "__main__":
    main()
