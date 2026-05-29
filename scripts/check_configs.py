#!/usr/bin/env python3
import os
import time
import json
import base64
import random
import re
import requests

GITHUB_SOURCES = [
    # ── Крупные агрегаторы (собирают из множества источников) ──
    {
        "name": "barry-far-all",
        "urls": ["https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt"]
    },
    {
        "name": "barry-far-sub6",
        "urls": ["https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub6.txt"]
    },
    {
        "name": "barry-far-sub7",
        "urls": ["https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub7.txt"]
    },
    {
        "name": "soroushmirzaei-vless",
        "urls": ["https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless"]
    },
    {
        "name": "soroushmirzaei-ipv6",
        "urls": ["https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/ipv6"]
    },
    {
        "name": "soroushmirzaei-russia",
        "urls": ["https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/countries/ru/mixed"]
    },
    {
        "name": "soroushmirzaei-russia-vless",
        "urls": ["https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/countries/ru/vless"]
    },
    {
        "name": "mahdibland-vless",
        "urls": ["https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_vless.txt"]
    },
    {
        "name": "mahdibland-all",
        "urls": ["https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"]
    },
    # ── REALITY конфиги ──
    {
        "name": "lagzian-reality",
        "urls": ["https://raw.githubusercontent.com/lagzian/SS-Collector/main/VLESS/reality.txt"]
    },
    {
        "name": "lagzian-vless",
        "urls": ["https://raw.githubusercontent.com/lagzian/SS-Collector/main/VLESS/vless.txt"]
    },
    {
        "name": "lagzian-ipv6",
        "urls": ["https://raw.githubusercontent.com/lagzian/SS-Collector/main/VLESS/ipv6.txt"]
    },
    {
        "name": "coldwater-reality",
        "urls": ["https://raw.githubusercontent.com/coldwater-10/V2rayCollector/main/vless_reality.txt"]
    },
    {
        "name": "coldwater-vless",
        "urls": ["https://raw.githubusercontent.com/coldwater-10/V2rayCollector/main/vless.txt"]
    },
    {
        "name": "ALIILAPRO",
        "urls": ["https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt"]
    },
    {
        "name": "MrMohebi-vless",
        "urls": ["https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/row-url/vless.txt"]
    },
    {
        "name": "Epodonios-vless",
        "urls": ["https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Configs/vless.txt"]
    },
    {
        "name": "yebekhe-vless",
        "urls": ["https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless"]
    },
    {
        "name": "mfuu-vless",
        "urls": ["https://raw.githubusercontent.com/mfuu/v2ray/master/vless.txt"]
    },
    {
        "name": "peasoft",
        "urls": ["https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt"]
    },
    {
        "name": "freefq",
        "urls": ["https://raw.githubusercontent.com/freefq/free/master/v2"]
    },
    {
        "name": "vpei",
        "urls": ["https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/o/node.txt"]
    },
    {
        "name": "tbbatbb",
        "urls": ["https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt"]
    },
    {
        "name": "arshiacomplus",
        "urls": ["https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/vless.txt"]
    },
    {
        "name": "awesome-vpn",
        "urls": ["https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all"]
    },
    {
        "name": "w1770938096",
        "urls": ["https://raw.githubusercontent.com/w1770938096/proxy/main/vless.txt"]
    },
    {
        "name": "HW7X-vless",
        "urls": ["https://raw.githubusercontent.com/HW7X/vless-config/main/vless.txt"]
    },
    {
        "name": "rxn957",
        "urls": ["https://raw.githubusercontent.com/rxn957/rxn957/main/vless.txt"]
    },
    {
        "name": "aiboboxx-vless",
        "urls": ["https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"]
    },
    {
        "name": "ermaozi-vless",
        "urls": ["https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/vless.txt"]
    },
    {
        "name": "mheidari98-vless",
        "urls": ["https://raw.githubusercontent.com/mheidari98/.proxy/main/vless"]
    },
    {
        "name": "saeeddev94-vless",
        "urls": ["https://raw.githubusercontent.com/saeeddev94/xray-boot/master/vless.txt"]
    },
    {
        "name": "roosterkid-vless",
        "urls": ["https://raw.githubusercontent.com/roosterkid/openproxylist/main/VLESS_RAW.txt"]
    },
    {
        "name": "Pawdroid-vless",
        "urls": ["https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"]
    },
    {
        "name": "zhangkaiitugithub",
        "urls": ["https://raw.githubusercontent.com/zhangkaiitugithub/passcro/main/speednodes.yaml"]
    },
    {
        "name": "Leon406-vless",
        "urls": ["https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/vless"]
    },
    {
        "name": "resasanian-vless",
        "urls": ["https://raw.githubusercontent.com/resasanian/Mirza/main/vless.txt"]
    },
    {
        "name": "IranianCypherpunks",
        "urls": ["https://raw.githubusercontent.com/IranianCypherpunks/sub/main/vlessconfig"]
    },
    {
        "name": "SoliSpirit-vless",
        "urls": ["https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/main/vless.txt"]
    },
    {
        "name": "MatinKh98-vless",
        "urls": ["https://raw.githubusercontent.com/MatinKh98/v2ray-subscribe/main/subscribe/vless.txt"]
    },
]

OUTPUT_DIR = "configs"
MAX_CONFIGS = 500


def fetch(urls: list) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200 and len(r.text.strip()) > 20:
                print(f"    OK: {url}")
                return r.text.strip()
            else:
                print(f"    FAIL {r.status_code}: {url}")
        except Exception as e:
            print(f"    ERROR: {url} — {e}")
    return ""


def decode_base64(data: str) -> str:
    clean = "".join(data.split())
    clean += '=' * (-len(clean) % 4)
    try:
        return base64.b64decode(clean).decode('utf-8', errors='ignore')
    except Exception:
        return ""


def is_ipv6(cfg: str) -> bool:
    return bool(re.search(r'@\[([0-9a-fA-F:]+)\]', cfg))


def extract_vless(text: str) -> list:
    result = []
    seen = set()
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("vless://") and "@" in line:
            if line not in seen:
                seen.add(line)
                result.append(line)
    found = re.findall(r'vless://[A-Za-z0-9\-]+@[^\s\'"<>&\n]+', text)
    for cfg in found:
        cfg = cfg.replace("&amp;", "&")
        if cfg not in seen:
            seen.add(cfg)
            result.append(cfg)
    return result


def main():
    print("=== СТАРТ ===")
    start = time.time()
    unique = set()
    ipv6_configs = set()

    print("\n── Загрузка источников ──")
    for source in GITHUB_SOURCES:
        name = source["name"]
        print(f"\n[{name}]")
        raw = fetch(source["urls"])

        if not raw:
            print(f"  Пропущен — не загрузился")
            continue

        extracted = extract_vless(raw)

        if not extracted:
            decoded = decode_base64(raw)
            if decoded:
                extracted = extract_vless(decoded)

        if extracted:
            ipv6_found = [c for c in extracted if is_ipv6(c)]
            ipv4_found = [c for c in extracted if not is_ipv6(c)]
            print(f"  Найдено: {len(extracted)} (IPv4: {len(ipv4_found)}, IPv6: {len(ipv6_found)})")
            unique.update(extracted)
            ipv6_configs.update(ipv6_found)
        else:
            print(f"  VLESS строк не найдено")

    configs = list(unique)
    ipv6_list = list(ipv6_configs)

    print(f"\nВсего уникальных: {len(configs)}")
    print(f"Из них IPv6: {len(ipv6_list)}")

    if len(configs) > MAX_CONFIGS:
        ipv6_quota = min(len(ipv6_list), MAX_CONFIGS // 5)
        ipv4_quota = MAX_CONFIGS - ipv6_quota
        ipv4_configs = [c for c in configs if not is_ipv6(c)]
        random.shuffle(ipv4_configs)
        random.shuffle(ipv6_list)
        configs = ipv4_configs[:ipv4_quota] + ipv6_list[:ipv6_quota]
        random.shuffle(configs)
        print(f"Обрезано до {MAX_CONFIGS} (IPv4: {ipv4_quota}, IPv6: {ipv6_quota})")

    if not configs:
        configs = ["vless://00000000-0000-0000-0000-000000000000@127.0.0.1:443?encryption=none&security=tls#No_Configs_Found"]

    plain = "\n".join(sorted(configs)) + "\n"
    b64 = base64.b64encode(plain.encode()).decode()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(f"{OUTPUT_DIR}/vless_plain.txt", "w") as f:
        f.write(plain)
    with open(f"{OUTPUT_DIR}/vless_base64.txt", "w") as f:
        f.write(b64)

    if ipv6_list:
        ipv6_plain = "\n".join(sorted(ipv6_list)) + "\n"
        ipv6_b64 = base64.b64encode(ipv6_plain.encode()).decode()
        with open(f"{OUTPUT_DIR}/vless_ipv6_plain.txt", "w") as f:
            f.write(ipv6_plain)
        with open(f"{OUTPUT_DIR}/vless_ipv6_base64.txt", "w") as f:
            f.write(ipv6_b64)
    else:
        open(f"{OUTPUT_DIR}/vless_ipv6_plain.txt", "w").close()
        open(f"{OUTPUT_DIR}/vless_ipv6_base64.txt", "w").close()

    stats = {
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_configs": len(configs),
        "ipv6_configs": len(ipv6_list),
        "ipv4_configs": len([c for c in configs if not is_ipv6(c)]),
        "elapsed_seconds": round(time.time() - start, 2)
    }
    with open(f"{OUTPUT_DIR}/stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nГотово! Сохранено: {len(configs)} конфигов")


if __name__ == "__main__":
    main()
