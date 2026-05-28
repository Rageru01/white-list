#!/usr/bin/env python3
"""
Собирает CIDR (IP-диапазоны) и SNI (домены) из популярных российских источников,
объединяет, дедуплицирует и сохраняет.
"""
import urllib.request, os, time, json

# ── Источники CIDR (IP-диапазоны) ─────────────────────────────────────────
CIDR_SOURCES = [
    ("igareck [all CIDR]",
     "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-all.txt"),
    ("igareck [checked CIDR — VK/YA/CDN/Beeline]",
     "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt"),
    ("antifilter.download [IP list]",
     "https://community.antifilter.download/list/ip.lst"),
    ("antifilter.download [суммарный IP]",
     "https://community.antifilter.download/list/summarized.lst"),
    ("1andrevich Re-filter-lists [ipsets all]",
     "https://raw.githubusercontent.com/1andrevich/Re-filter-lists/main/ipsets_all.lst"),
    ("nicklvsa russia-blocked [CIDR]",
     "https://raw.githubusercontent.com/nicklvsa/russia-blocked/main/russia.cidr"),
    ("zhongfly runet-ip [CIDR]",
     "https://raw.githubusercontent.com/zhongfly/runet-ip/main/russia-cidr.txt"),
    ("ipverse ru [CIDR]",
     "https://raw.githubusercontent.com/ipverse/rir-ip/master/country/ru/ipv4-aggregated.txt"),
]

# ── Источники SNI (домены) ─────────────────────────────────────────────────
SNI_SOURCES = [
    ("igareck [all SNI]",
     "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-SNI-RU-all.txt"),
    ("antifilter.download [domains]",
     "https://community.antifilter.download/list/domains.lst"),
    ("1andrevich Re-filter-lists [domains all]",
     "https://raw.githubusercontent.com/1andrevich/Re-filter-lists/main/domains_all.lst"),
    ("1andrevich Re-filter-lists [domains lite]",
     "https://raw.githubusercontent.com/1andrevich/Re-filter-lists/main/lists/domains_lite.lst"),
    ("nicklvsa russia-blocked [domains]",
     "https://raw.githubusercontent.com/nicklvsa/russia-blocked/main/russia-domains.txt"),
    ("dartraiden no-Russia-hosts [domains]",
     "https://raw.githubusercontent.com/dartraiden/no-Russia-hosts/master/hosts.txt"),
    ("zapret-info z-i [csv domains]",
     "https://raw.githubusercontent.com/zapret-info/z-i/master/dump.csv"),
]

OUTPUT_DIR = "configs"


def fetch(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [WARN] {url.split('/')[-1]}: {e}")
        return ""


def is_cidr(line: str) -> bool:
    import re
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$", line.strip()))


def is_domain(line: str) -> bool:
    import re
    line = line.strip().lstrip(".")
    return bool(re.match(
        r"^(?!\-)([a-zA-Z0-9\-]{1,63}\.)+[a-zA-Z]{2,}$", line
    )) and not line.startswith("#")


def parse_domains_from_csv(text: str) -> list:
    """Парсит домены из dump.csv zapret-info."""
    domains = []
    for line in text.splitlines():
        parts = line.split(";")
        if len(parts) >= 2:
            raw = parts[1].strip().strip('"').lower()
            for d in raw.split("|"):
                d = d.strip().lstrip("*.")
                if is_domain(d):
                    domains.append(d)
    return domains


def collect(sources: list, mode: str) -> set:
    result = set()
    for name, url in sources:
        raw = fetch(url)
        if not raw:
            continue
        lines = raw.splitlines()

        if "dump.csv" in url:
            items = parse_domains_from_csv(raw)
        elif mode == "cidr":
            items = [l.strip() for l in lines if is_cidr(l)]
        else:
            items = []
            for l in lines:
                l = l.strip().lstrip("*.").lower()
                # пропустить IP-адреса и комментарии
                if l.startswith("#") or not l:
                    continue
                # убрать строки вида "0.0.0.0 domain.ru" (hosts формат)
                parts = l.split()
                candidate = parts[-1] if len(parts) > 1 else l
                if is_domain(candidate):
                    items.append(candidate)

        added = len(items) - len(result)
        result.update(items)
        added_after = len(result) - (len(result) - len(items))
        print(f"  +{len(items):6d}  {name}")

    return result


def save(filename: str, items: set, sort: bool = True):
    lines = sorted(items) if sort else list(items)
    path = f"{OUTPUT_DIR}/{filename}"
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  {filename}: {len(lines)} записей")
    return len(lines)


def main():
    print(f"=== CIDR + SNI Collector ===\n")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start = time.time()

    # ── CIDR ──────────────────────────────────────────────────────────────
    print(f"[1/2] Сбор CIDR из {len(CIDR_SOURCES)} источников...")
    cidr = collect(CIDR_SOURCES, "cidr")
    print(f"  Итого уникальных CIDR: {len(cidr)}\n")

    # ── SNI ───────────────────────────────────────────────────────────────
    print(f"[2/2] Сбор SNI (доменов) из {len(SNI_SOURCES)} источников...")
    sni = collect(SNI_SOURCES, "sni")
    print(f"  Итого уникальных доменов: {len(sni)}\n")

    # ── Сохранение ────────────────────────────────────────────────────────
    print("Сохранение...")
    n_cidr = save("CIDR-RU-all.txt", cidr)
    n_sni  = save("SNI-RU-all.txt",  sni)

    stats = {
        "last_updated":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cidr_sources":  len(CIDR_SOURCES),
        "sni_sources":   len(SNI_SOURCES),
        "cidr_total":    n_cidr,
        "sni_total":     n_sni,
        "elapsed_seconds": round(time.time() - start, 1),
    }
    with open(f"{OUTPUT_DIR}/stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nГотово. CIDR: {n_cidr}, SNI: {n_sni}")


if __name__ == "__main__":
    main()
