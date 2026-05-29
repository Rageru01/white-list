#!/usr/bin/env python3
import os
import time
import json
import base64
import random
import requests

# ── Стабильные альтернативные источники (включая зеркала и API) ──
VLESS_SOURCES = [
    ("NodeFree-Sub", "https://nodefree.org/dy/vless.txt"),
    ("V2rayShare", "https://raw.fastgit.org/v2raypool/modules/main/vless.txt"),
    ("FreeSub-API", "https://sub.f789.xyz/sub?target=vless")
]

OUTPUT_DIR = "configs"
MAX_CONFIGS = 200


def fetch(url: str) -> str:
    """Скачивает данные с таймаутом и обходом базовых блокировок"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.text.strip()
        return ""
    except Exception:
        return ""


def decode_base64(data: str) -> str:
    """Безопасно декодирует Base64 конфигурации"""
    clean_data = "".join(data.split())
    missing_padding = len(clean_data) % 4
    if missing_padding:
        clean_data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(clean_data).decode('utf-8', errors='ignore')
    except Exception:
        return data


def is_vless(line: str) -> bool:
    """Проверка строки на формат VLESS"""
    line = line.strip()
    return line.startswith("vless://") and "@" in line


def collect_vless(sources: list) -> set:
    """Собирает и декодирует конфигурации"""
    result = set()
    
    for name, url in sources:
        raw = fetch(url)
        if not raw or len(raw) < 15:
            continue
            
        # Если пришел закодированный текст, расшифровываем
        if "vless://" not in raw[:200]:
            raw = decode_base64(raw)
            
        lines = raw.splitlines()
        source_configs = []
        
        for line in lines:
            line = line.strip()
            if is_vless(line):
                source_configs.append(line)
                
        if source_configs:
            print(f"  [+] {name}: Найдено {len(source_configs)} строк.")
            result.update(source_configs)
        
    return result


def save_subscriptions(configs: set):
    """Ограничивает количество до 200 и сохраняет файлы"""
    configs_list = list(configs)
    
    if len(configs_list) > MAX_CONFIGS:
        random.shuffle(configs_list)
        configs_list = configs_list[:MAX_CONFIGS]
        print(f"  [*] Лимит превышен. Выбрано {MAX_CONFIGS} случайных конфигов.")
        
    if not configs_list:
        # Резервная ссылка на случай полного отсутствия сети
        configs_list = ["vless://00000000-0000-0000-0000-000000000000@127.0.0.1:443?encryption=none&security=tls#No_Configs_Available_Try_Update_Later"]

    plain_text = "\n".join(sorted(configs_list)) + "\n"
    b64_text = base64.b64encode(plain_text.encode('utf-8')).decode('utf-8')
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(f"{OUTPUT_DIR}/vless_plain.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
        
    with open(f"{OUTPUT_DIR}/vless_base64.txt", "w", encoding="utf-8") as f:
        f.write(b64_text)
        
    return len(configs_list)


def main():
    print("=== ЗАПУСК СБОРЩИКА VLESS ===")
    start = time.time()

    vless_configs = collect_vless(VLESS_SOURCES)
    total_saved = save_subscriptions(vless_configs)

    stats = {
        "last_updated":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "vless_sources":   len(VLESS_SOURCES),
        "total_configs":   total_saved,
        "elapsed_seconds": round(time.time() - start, 1),
    }
    
    with open(f"{OUTPUT_DIR}/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print(f"Сохранено конфигураций: {total_saved}")


if __name__ == "__main__":
    main()
    
