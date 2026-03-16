# Рефакторинг Verboten

## Цель
- Портфолио — показать "взрослый" подход к разработке
- Разобраться в коде, написанном нейросетью

---

## Текущие проблемы

### `app/config.py` (оценка: 6/10)

- [ ] Inconsistency: `os.environ.get()` vs `os.getenv()` — выбрать одно
- [ ] Нет fallback для `SECRET_KEY` — если не задан в env, приложение упадёт
- [ ] Строки 7, 16, 17 используют `os.environ.get()`, а 18, 19 — `os.getenv()`

**Решение:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
```

---

### `app/__init__.py` (оценка: 7/10)

- [ ] Потеряны параметры SocketIO из app_old.py:
  - `cors_allowed_origins='*'`
  - `async_mode='threading'`
  - `manage_session=False`
  - `ping_timeout=60`
  - `ping_interval=25`
- [ ] Глобальный `socketio` — проблема для тестирования

---

### `app/routes/auth.py` (оценка: 5/10)

- [ ] Дублирование: три раза `Config.TWITCH_CLIENT_ID`, `Config.TWITCH_REDIRECT_URI`
- [ ] Нет try/except — если `requests.post` упадёт, будет 500
- [ ] `response.json()` без проверки — Twitch может вернуть не JSON
- [ ] `user_data['data'][0]` — если `data` пустой, `IndexError`
- [ ] Пустая строка 77 — мусор

---

### `app/routes/api.py` (оценка: 8/10)

- [ ] Хрупкий путь к файлу:
  ```python
  file_path = BASE_DIR / '..' / '..' / 'data' / 'words.json'
  ```
- [ ] Файл открывается каждый запрос — нет кэширования
- [ ] Нет try/except — если файл не найден или битый JSON, будет 500

---

## Не перенесено из app_old.py

### `app/services/twitch_irc.py` — ПУСТОЙ

Нужно перенести:
- [ ] `connect_to_twitch()` — async подключение к Twitch IRC
- [ ] `parse_twitch_message()` — парсинг сообщений
- [ ] `twitch_connections` dict + `connections_lock`
- [ ] `start_twitch_connection()` / `stop_twitch_connection()`

### `app/sockets/twitch_chat.py` — ПУСТОЙ

Нужно перенести:
- [ ] Socket.IO handler `connect_chat`
- [ ] Socket.IO handler `disconnect_chat`
- [ ] Связь с twitch_irc сервисом

---

## Следующие шаги (предложение)

1. Перенести WebSocket логику в модульную структуру
2. Добавить error handling везде
3. Добавить логирование (logging)
4. Написать тесты
5. Добавить type hints
6. Docker / docker-compose

---

## Вопросы для изучения

- Зачем `threading` + `asyncio` вместе в старом коде?
- Как правильно шарить `socketio` между модулями?
- Как тестировать Flask + SocketIO?
