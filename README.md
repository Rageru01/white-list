# VLESS Reality White List

Автоматически собирает VLESS конфиги из 20+ источников через GitHub и CDN-зеркала,
проверяет каждый сервер на доступность и сохраняет только рабочие.
Обновляется каждые 6 часов без участия пользователя.

## Ссылки для VPN-клиента

Все рабочие конфиги:
https://raw.githubusercontent.com/Rageru01/white-list/main/configs/working_sub.txt

Только Reality (рекомендуется для России):
https://raw.githubusercontent.com/Rageru01/white-list/main/configs/working_reality_sub.txt

## Как добавить подписку в клиент

v2rayNG (Android):
Нижнее меню → Подписки → + → вставить ссылку → Обновить

Hiddify (Android / iOS):
+ → Добавить профиль → вставить ссылку

v2rayN (Windows):
Подписки → Настройки подписок → Добавить → вставить ссылку → Обновить

Streisand (iOS):
Настройки → Импорт из URL → вставить ссылку

## Файлы

configs/working_sub.txt          — все рабочие (base64 подписка)
configs/working_reality_sub.txt  — только Reality (base64 подписка)
configs/working_regular_sub.txt  — только обычные VLESS (base64 подписка)
configs/working_reality.txt      — Reality plain text
configs/working.txt              — все рабочие plain text
configs/stats.json               — статистика последней проверки

## Источники

Конфиги берутся из популярных открытых репозиториев через GitHub и CDN-зеркала:

- igareck/vpn-configs-for-russia — Reality белые списки для России
- soroushmirzaei/telegram-configs-collector — 100+ Telegram каналов
- yebekhe/TelegramV2rayCollector — агрегатор Telegram
- itsyebekhe/HiN-VPN, ConfigHub
- barry-far/V2ray-Configs
- Epodonios/v2ray-configs
- peasoft/NoMoreVPN
- mahdibland/V2RayAggregator
- и другие

Дублирующие источники получают данные через CDN (rawcdn.githack.com)
для надёжности в случае если основной адрес недоступен.

## Как устроено

1. Из каждого источника берётся случайная выборка до 150 VLESS конфигов
2. К каждому серверу проверяется TCP/TLS соединение (таймаут 5 сек)
3. Reality конфиги сортируются по скорости и идут первыми
4. Результат сохраняется в configs/ и коммитится автоматически

## Обновление

Автоматически каждые 6 часов через GitHub Actions.
Ручной запуск: Actions → Update Working Configs → Run workflow.
