#!/usr/bin/env python3
import base64, socket, ssl, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import json, os, time, random

# Источники с упором на VLESS Reality и белые списки для России
SOURCES = [
    # ── igareck — лучшие Reality для России (белые списки) ────────────────
    ("igareck [Reality Mobile 150 лучших #1]",
     "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt"),
    ("igareck [Reality Mobile 150 лучших #2]",
     "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt"),

    # ── Крупнейшие агрегаторы с Reality конфигами ─────────────────────────
    ("soroushmirzaei [vless — 100+ TG каналов]",
     "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless"),
    ("soroushmirzaei [splitted vless]",
     "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/subscribe/protocols/vless"),
    ("yebekhe TelegramV2rayCollector [vless]",
     "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/vless"),
    ("yebekhe HiN-VPN [mix]",
     "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription/normal/mix"),
    ("yebekhe ConfigHub",
     "https://raw.githubusercontent.com/yebekhe/ConfigHub/main/Eternity/normal/mix"),
    ("yebekhe PSG",
     "https://raw.githubusercontent.com/itsyebekhe/PSG/main/subscriptions/xray/normal/mix"),

    # ── barry-far — известный агрегатор с Reality ─────────────────────────
    ("barry-far [vless only]",
     "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vless.txt"),
    ("barry-far [all configs]",
     "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt"),

    # ── Epodonios — содержит Reality конфиги ──────────────────────────────
    ("Epodonios [vless only]",
     "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt"),
    ("Epodonios [all]",
     "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt"),

    # ── Россия-фокус ───────────────────────────────────────────────────────
    ("peasoft NoMoreVPN [RU]",
     "https://raw.githubusercontent.com/peasoft/NoMoreVPN/master/subscriptions/raw.txt"),
    ("mahdibland V2RayAggregator",
     "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity.txt"),
    ("Surfboardv2ray [sorted vless]",
     "https://raw.githubusercontent.com/Surfboardv2ray/Proxy-sorter/main/subdata/sorted/vless"),
    ("SoliSpirit [vless]",
     "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/Protocols/vless.txt"),
    ("MhdiTaheri V2rayCollector",
     "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector/main/vless"),
    ("Leon406 SubCrawler [vless]",
     "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/vless"),
    ("ALIILAPRO v2ray",
     "https://raw.githubusercontent.com/ALIILAPRO/v2ray/main/sub.txt"),
    ("vveg26 chromego_merge",
     "https://raw.githubusercontent.com/vveg26/chromego_merge/main/sub/merged_proxies_new.txt"),
]

OUTPUT_DIR  = "configs"
TIMEOUT     = 4
MAX_WORKERS = 100
PER_SOURCE  = 150


def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [WARN] {url.split('/')[-1]}: {e}")
        return ""


def decode_lines(text):
    text = text.strip()
    if not text:
        return []
    try:
        decoded = base64.b64decode(text + "==").decode("utf-8", errors="ignore")
        lines = [l.strip() for l in decoded.splitlines() if l.strip()]
        if any(l.startswith(("vless://", "vmess://", "trojan://")) for l in lines):
            return lines
    except Exception:
        pass
    return [l.strip() for l in text.splitlines() if l.strip()]


def parse_vless(uri):
    try:
        rest = uri[len("vless://"):]
        at = rest.rfind("@")
        if at == -1:
            return None
        host_part = rest[at + 1:]
        for sep in ("?", "#", "/"):
            i = host_part.find(sep)
            if i != -1:
                host_part = host_part[:i]
        if host_part.startswith("["):
            b = host_part.find("]")
            return host_part[1:b], int(host_part[b + 2:])
        if ":" in host_part:
            h, p = host_part.rsplit(":", 1)
            return h, int(p)
    except Exception:
        pass
    return None


def measure_tcp(host, port):
    try:
        t0 = time.monotonic()
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return time.monotonic() - t0
    except Exception:
        return None


def measure_tls(host, port):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        t0 = time.monotonic()
        with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return time.monotonic() - t0
    except Exception:
        return None


def check_config(uri):
    parsed = parse_vless(uri)
    if not parsed:
        return uri, None
    host, port = parsed
    t = measure_tcp(host, port)
    if t is None:
        t = measure_tls(host, port)
    return uri, (round(t * 1000) if t is not None else None)


def is_reality(uri):
    return "security=reality" in uri or "reality" in uri.lower()


def save_txt(name, lines):
    with open(f"{OUTPUT_DIR}/{name}", "w") as f:
        f.write("\n".join(lines) + "\n" if lines else "")
    print(f"  {name}: {len(lines)} конфигов")


def save_sub(name, lines):
    if not lines:
        return
    enc = base64.b64encode("\n".join(lines).encode()).decode()
    with open(f"{OUTPUT_DIR}/{name}", "w") as f:
        f.write(enc)
    print(f"  {name}: base64 ({len(lines)} конфигов)")


def main():
    print(f"=== VLESS Reality Checker | {len(SOURCES)} источников, до {PER_SOURCE} с каждого ===\n")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[1/3] Сбор конфигов...")
    all_vless = set()
    for name, url in SOURCES:
        raw = fetch_url(url)
        if not raw:
            continue
        lines = decode_lines(raw)
        vless = [l for l in lines if l.startswith("vless://")]
        if not vless:
            print(f"  +  0  {name} [нет vless]")
            continue
        if len(vless) > PER_SOURCE:
            vless = random.sample(vless, PER_SOURCE)
        print(f"  +{len(vless):3d}  {name}")
        all_vless.update(vless)

    configs = list(all_vless)
    reality = [c for c in configs if is_reality(c)]
    regular = [c for c in configs if not is_reality(c)]
    print(f"\n  Всего: {len(configs)} (reality={len(reality)}, regular={len(regular)})\n")

    if not configs:
        print("Конфиги не найдены.")
        sys.exit(0)

    print(f"[2/3] Проверка {len(configs)} конфигов...")
    results = []
    done = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_config, uri): uri for uri in configs}
        for future in as_completed(futures):
            uri, lat = future.result()
            results.append((uri, lat))
            done += 1
            if done % 200 == 0 or done == len(configs):
                working = sum(1 for _, l in results if l)
                print(f"  {done}/{len(configs)} | Рабочих: {working}")

    elapsed = round(time.time() - start, 1)

    working_reality = sorted(
        [(u, l) for u, l in results if l is not None and is_reality(u)],
        key=lambda x: x[1]
    )
    working_regular = sorted(
        [(u, l) for u, l in results if l is not None and not is_reality(u)],
        key=lambda x: x[1]
    )
    all_working = [u for u, _ in working_reality] + [u for u, _ in working_regular]

    print(f"\n  Рабочих: {len(all_working)} из {len(configs)} за {elapsed}с\n")

    print("[3/3] Сохранение...")
    save_txt("working.txt",             all_working)
    save_sub("working_sub.txt",         all_working)
    save_txt("working_reality.txt",     [u for u, _ in working_reality])
    save_sub("working_reality_sub.txt", [u for u, _ in working_reality])
    save_txt("working_regular.txt",     [u for u, _ in working_regular])
    save_sub("working_regular_sub.txt", [u for u, _ in working_regular])

    stats = {
        "last_updated":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources":         len(SOURCES),
        "per_source":      PER_SOURCE,
        "total_checked":   len(configs),
        "working_total":   len(all_working),
        "working_reality": len(working_reality),
        "working_regular": len(working_regular),
        "elapsed_seconds": elapsed,
    }
    with open(f"{OUTPUT_DIR}/stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print("\nГотово.")


if __name__ == "__main__":
    main()
