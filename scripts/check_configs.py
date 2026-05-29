#!/usr/bin/env python3
import urllib.request
import os
import time
import json
import base64

# ── 100% Рабочие, быстрые и легковесные источники VLESS ───────────────────
VLESS_SOURCES = [
    ("HopV2ray", 
     "https://raw.githubusercontent.com/hopv2ray/HopV2ray/main/vless.txt"),
    ("V2rayNoah", 
     "https://raw.githubusercontent.com/V2rayNoah/Nodes/main/vless.txt"),
    ("Snakem72", 
     "https://raw.githubusercontent.com/snakem72/v2ray/main/vless.txt"),
    ("LalatinaSub", 
     "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/vless")
]

OUTPUT_DIR = "configs"


def fetch(url: str) -> str:
    """Скачивает содержимое по ссылке с увеличенным таймаутом"""
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        # Увеличиваем таймаут до 40 секунд на случай долгого ответа GitHub
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", errors="ignore").strip()
    except Exception as e:
        print(f"  [WARN] Не удалось скачать {url.split('/')[-1][:30]}: {e}")
        return ""


def decode_base64(data: str) -> str:
    """Безопасно декодирует Base64 с исправлением паддинга"""
    clean_data = "".join(data.split())
    missing_padding = len(clean_data) % 4
    if missing_padding:
        clean_data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(clean_data).decode('utf-8', errors='ignore')
    except Exception:
        return data


def is_vless(line: str) -> bool:
    """Универсальная проверка VLESS строки"""
    line = line.strip()
    return line.startswith("vless://") and "@" in line


def collect_vless(sources: list) -> set:
    """Собирает, декодирует и фильтрует конфигурации"""
    result = set()
    
    for name, url in sources:
        raw = fetch(url)
        if not raw:
            print(f"  [-] {name}: Источник пуст или недоступен")
            continue
            
        print(f"  [*] {name}: Успешно скачано {len(raw)} символов текста.")
        
        # Умное определение формата (Plain Text или Base64)
        if "vless://" not in raw[:150]:
            print(f"  [*] {name}: Обнаружен формат Base64, декодируем...")
            raw = decode_base64(raw)
            
        lines = raw.splitlines()
        source_configs = []
        
        for line in lines:
            line = line.strip()
            if is_vless(line):
                source_configs.append(line)
                
        if not source_configs:
            print(f"  [!] {name}: Не найдено ни одной VLESS строки после проверки")
            continue
            
        print(f"  [+] {name}: Успешно распознано {len(source_configs)} конфигураций")
        result.update(source_configs)
        
    return result


def save_subscriptions(configs: set):
    """Сохраняет конфигурации в файлы"""
    lines = sorted(list(configs))
    plain_text = "\n".join(lines) + "\n"
    
    b64_bytes = base64.b64encode(plain_text.encode('utf-8'))
    b64_text = b64_bytes.decode('utf-8')
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(f"{OUTPUT_DIR}/vless_plain.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
        
    with open(f"{OUTPUT_DIR}/vless_base64.txt", "w", encoding="utf-8") as f:
        f.write(b64_text)
        
    print(f"\n  [Файлы успешно записаны на диск]:")
    print(f"  -> {OUTPUT_DIR}/vless_plain.txt ({len(lines)} строк)")
    print(f"  -> {OUTPUT_DIR}/vless_base64.txt (Закодирован в Base64)")
    return len(lines)


def main():
    print(f"=== СБОРЩИК VLESS ПОДПИСОК (IPv4 + IPv6) ===\n")
    start = time.time()

    print(f"[1/2] Сканирование открытых источников...")
    vless_configs = collect_vless(VLESS_SOURCES)
    print(f"\nИтого уникальных конфигураций собрано: {len(vless_configs)}")

    if not vless_configs:
        print("[ERROR] Итоговый список пуст! Запись отменена.")
        total_saved = 0
    else:
        print("[2/2] Сохранение результатов в папку...")
        total_saved = save_subscriptions(vless_configs)

    stats = {
        "last_updated":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "vless_sources":   len(VLESS_SOURCES),
        "total_configs":   total_saved,
        "elapsed_seconds": round(time.time() - start, 1),
    }
    
    with open(f"{OUTPUT_DIR}/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"\nРабота скрипта завершена за {stats['elapsed_seconds']} сек.")


if __name__ == "__main__":
    main()

