# VLESS Subscription Aggregator

Автоматический сборщик VLESS-конфигураций из 60+ источников: GitHub-агрегаторов и публичных Telegram-каналов.

Приоритет при отборе: **REALITY → Россия → IPv6 → остальные**. Обновляется каждые 6 часов через GitHub Actions.

---

## 🔗 Подписки

### Все конфиги (рекомендуется)

https://raw.githubusercontent.com/Rageru01/white-list/main/configs/vless_base64.txt

### Только REALITY — лучший обход DPI / РКН

https://raw.githubusercontent.com/Rageru01/white-list/main/configs/vless_reality_base64.txt

### Только российские серверы

https://raw.githubusercontent.com/Rageru01/white-list/main/configs/vless_russia_base64.txt

### Только IPv6

https://raw.githubusercontent.com/Rageru01/white-list/main/configs/vless_ipv6_base64.txt

> Plain-text версии доступны с суффиксом `_plain.txt` вместо `_base64.txt`.

---

## 📱 Как добавить подписку

**Hiddify:** Откройте Hiddify → **+** → **Добавить подписку по URL** → вставьте ссылку → **Сохранить** → обновить.

**v2rayNG:** **☰** → **Subscription group** → **+** → вставьте ссылку → **OK** → **☰** → **Update subscription**.

**Nekobox / NekoRay:** **Profiles** → **New group** → тип **Subscription** → вставьте ссылку → **OK** → правой кнопкой по группе → **Update**.

---

## 📦 Источники

### Telegram-каналы

| Канал | Особенность |
|-------|-------------|
| @v2ray_configs_pool | Самый большой пул, обновляется несколько раз в день |
| @VlessConfig | VLESS-only, высокое качество |
| @DirectVPN | Прямые конфиги |
| @proxy_mtn | Активный пул |
| @freev2rayssr / @FreeV2rays | Бесплатные конфиги |
| @ConfigsHUB | Агрегатор каналов |
| @PrivateVPNs | Приватные конфиги |
| @vless_vmess_v2rayng | Смешанный пул |
| @iP_CF | Cloudflare IP конфиги |
| @proxystore11 | Регулярные обновления |

### GitHub-агрегаторы

| Репозиторий | Особенность |
|-------------|-------------|
| soroushmirzaei/telegram-configs-collector | Парсит 100+ TG-каналов, разбивка по странам |
| MrMohebi/xray-proxy-grabber-telegram | Прямой парсинг Telegram |
| Surfboardv2ray/TGParse + Proxy-sorter | TG-парсер + сортировка по странам |
| yebekhe/TVC | Активен годами |
| Epodonios/v2ray-configs | Ежедневные обновления |
| barry-far/V2ray-Configs | Один из старейших агрегаторов |
| mahdibland/V2RayAggregator | Крупный merger |
| lagzian/SS-Collector | REALITY и IPv6 |
| coldwater-10/V2rayCollector | REALITY + Россия |

---

## 🔄 Автоматизация

Работает через GitHub Actions. По расписанию — каждые 6 часов. Вручную — Actions → *Update Working Configs* → **Run workflow**.

При каждом запуске скрипт загружает данные из 60+ источников, дедуплицирует по `uuid@host:port`, применяет квоты (REALITY 30% · Россия 25% · IPv6 15% · прочие 30%) и сохраняет до 1000 конфигов в 4 файла.

---

## 📊 Статистика последнего обновления

https://raw.githubusercontent.com/Rageru01/white-list/main/configs/stats.json
