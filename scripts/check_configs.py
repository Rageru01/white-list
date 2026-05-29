#!/usr/bin/env python3
import os
import time
import json
import base64
import random
import requests

# ── Лучшие и самые жирные базы (igareck, mahdibland, yebekhe) ────────────────
VLESS_SOURCES = [
    ("Igareck-Vless", 
     "https://raw.githubusercontent.com/igareck/vless/main/vless.txt"),
    ("Mahdibland-Merge", 
     "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"),
    ("Yebekhe-TVC", 
     "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless")
]

OUTPUT_DIR = "configs"
MAX_CONFIGS = 200


def fetch(url: str) -> str:
    """Скачивает сырые данные с серверов"""
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
    """Безопасно декодирует Base64 поток"""
    clean_data = "".join(data.split())
    missing_padding = len(clean_data) % 4
    if missing_padding:
        clean_data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(clean_data).decode('utf-8', errors='ignore')
    except Exception:
        return ""


def is_vless(line: str) -> bool:
    """Проверяет, является ли строка VLESS ссылкой"""
    line = line.strip()
    return line.startswith("vless://") and "@" in line


def extract_vless_from_text(text: str) -> list:
    """Вытаскивает все VLESS строки из любого текстового блока"""
    found = []
    for line in text.splitlines():
        line = line.strip()
        if is_vless(line):
            found.append(line)
    return found


def collect_vless(sources: list) -> set:
    """Собирает конфигурации, проверяя оба формата по очереди"""
    result = set()
    
    for name, url in sources:
        raw = fetch(url)
        if not raw or len(raw) < 10:
            continue
            
        # Способ 1: Пробуем распарсить как обычный текст
        source_configs = extract_vless_from_text(raw)
        
        # Способ 2: Если обычным текстом ничего не нашлось, пробуем декодировать из Base64
        if not source_configs:
            decoded = decode_base64(raw)
            if decoded:
                source_configs = extract_vless_from_text(decoded)
                
        if source_configs:
            print(f"  [+] {name}: Успешно вытащили {len(source_configs)} конфигураций.")
            result.update(source_configs)
        else:
            print(f"  [-] {name}: Не удалось извлечь прокси (пусто или не тот формат).")
        
    return result


def save_subscriptions(configs: set):
    """Ограничивает до 200 штук и сохраняет файлы подписок"""
    configs_list = list(configs)
    
    # Если серверов куча, перемешиваем и берем ровно 200 случайных
    if len(configs_list) > MAX_CONFIGS:
        random.shuffle(configs_list)
        configs_list = configs_list[:MAX_CONFIGS]
        print(f"  [*] Сработало ограничение: выбрано {MAX_CONFIGS} случайных прокси.")
        
    if not configs_list:
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
    print("=== ОБНОВЛЕННЫЙ ТАРАННЫЙ ПАРСЕР VLESS ===")
    start = time.time()

    vless_configs = collect_vless(VLESS_SOURCES)
    print(f"\nВсего уникальных конфигураций в обработке: {len(vless_configs)}")

    total_saved = save_subscriptions(vless_configs)

    stats = {
        "last_updated":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "vless_sources":   len(VLESS_SOURCES),
        "total_configs":   total_saved,
        "elapsed_seconds": round(time.time() - start, 1),
    }
    
    with open(f"{OUTPUT_DIR}/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print(f"Готово! Записано в файлы подписок: {total_saved}")


if __name__ == "__main__":
    main()
    
