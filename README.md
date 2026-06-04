# MAX-AI

MAX-AI — это консольный AI-ассистент на Python. Он позволяет задавать вопросы в терминале, автоматически извлекать ссылки из текста и анализировать контент веб-страниц, документов и YouTube.

## Что это за проект

Этот проект предназначен для тех, кто хочет получать краткие ответы от AI без перехода в браузер. MAX-AI:

- автоматически находит URL в тексте запроса;
- загружает страницы и файлы;
- извлекает текст из PDF, DOCX, PPTX, XLSX, XLS, TXT, MD;
- вытаскивает субтитры и метаданные YouTube;
- кэширует ответы;
- сохраняет историю запросов.

## Структура репозитория

Корневая структура проекта сейчас разделена на три папки:

- `src/` — основной исходный код проекта;
- `config/` — конфигурация и файлы окружения;
- `project/` — упаковка проекта и документация.

Внутри `src/` находится:

```
src/max_ai/
├── cli.py
├── commands/
├── core/
├── constants.py
├── models/
└── utils/
```

## Требования

- Python 3.9+
- Интернет для загрузки URL и YouTube
- API-ключ Cohere
- (Опционально) API-ключ Mistral для улучшенных ответов

## Быстрая установка

### 1. Установка через pip

```bash
pip install max-ai
```

### 2. Автоматическое добавление в PATH

#### Для Windows:
Запустите скрипт `install.ps1`:
```powershell
."C:\Users\user\Desktop\MAX-AI\install.ps1"
```

#### Для Linux/macOS:
Запустите скрипт `install.sh`:
```bash
chmod +x install.sh
./install.sh
```

### 3. Проверка установки

```bash
max-ai --help
```

Если команда не работает, перезапустите терминал.

## Ручная установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/max-ai.git
cd max-ai
```

### 2. Создайте виртуальное окружение

```bash
python -m venv .venv
```

#### Unix / macOS

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate
```

### 3. Установите пакет

```bash
cd project
pip install -e .
```

### 4. Добавьте путь к Scripts в PATH

#### Для Windows:
```powershell
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$env:USERPROFILE\AppData\Local\Programs\Python\Python313\Scripts", "User")
```

#### Для Linux/macOS:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Проверка установки

```bash
max-ai --help
```

> Если команда `max-ai` не найдена, скорее всего, `Scripts` каталог текущего Python не добавлен в PATH.

## Настройка окружения

Скопируйте шаблон конфигурации:

```bash
cp config/.env.example config/.env
```

Откройте `config/.env` и заполните свои ключи:

```dotenv
COHERE_API_KEY=your_cohere_api_key
MISTRAL_API_KEY=your_mistral_api_key  # опционально
```

### Windows

Если вы используете PowerShell, команда будет выглядеть так:

```powershell
Copy-Item config\.env.example config\.env
```

## Конфигурация YAML

Файл `config/max-ai.yaml` (или `max-ai.yaml` в корне репозитория) позволяет настраивать параметры:

```yaml
cohere_model: "command-a-03-2025"
mistral_model: "mistral-large-latest"
max_content_length: 50000
summarize_threshold: 40000
cache_ttl: 3600
timeout: 30
max_retries: 3
rate_limit: 5
system_prompt: "Ты — полезный ассистент."
mistral_system_prompt: "Ты — опытный ассистент, который улучшает ответы."
```

### Что означают параметры

- `cohere_model` — модель Cohere для основного ответа.
- `mistral_model` — модель Mistral для доработки ответа.
- `max_content_length` — максимальный размер текста из источника.
- `summarize_threshold` — порог, выше которого содержимое автоматически суммируется.
- `cache_ttl` — время хранения кеша в секундах.
- `timeout` — общий таймаут сетевых запросов.
- `max_retries` — число попыток при ошибках загрузки.
- `rate_limit` — максимум одновременных запросов.
- `system_prompt` — системный промпт для Cohere.
- `mistral_system_prompt` — системный промпт для Mistral.

## Запуск

### Основные команды

```bash
max-ai run "Привет, как дела?"
max-ai interactive
max-ai history
max-ai history --limit 5
max-ai history-clear
max-ai cache-clear
max-ai status
max-ai status --days 30
```

### Примеры запросов

```bash
max-ai run "Что написано на этом сайте? https://example.com"
max-ai run "Прочитай этот PDF и сделай резюме https://example.com/document.pdf"
max-ai run "Прочитай этот Word-документ https://example.com/document.docx"
max-ai run "О чем это видео? https://www.youtube.com/watch?v=example"
```

### Интерактивный режим

```bash
max-ai interactive
```

В интерактивном режиме вы можете вводить вопросы напрямую в консоль. Для выхода введите `exit`.

### Полезные параметры

- `--no-cache` — не использовать кеш.
- `--cohere-key YOUR_KEY` — использовать указанный ключ Cohere.
- `--ttl 7200` — задать TTL кеша в секундах.
- `--source URL` — добавить дополнительный источник.
- `--verbose` — включить подробный вывод.
- `--config config/max-ai.yaml` — явно указать файл конфигурации.

## Как работает MAX-AI

1. CLI команда принимает текст запроса.
2. Внутри запроса автоматически ищутся ссылки по шаблону `https?://\S+`.
3. Для каждого URL загружается содержимое:
   - HTML-страницы
   - PDF
   - DOCX
   - PPTX
   - XLSX/XLS
   - TXT/MD
   - YouTube
4. Текст объединяется с оригинальным запросом и историей.
5. Отправляется запрос в Cohere.
6. При наличии Mistral-ключа ответ может дорабатываться Mistral.
7. Результат сохраняется в кеш и историю.

## Особенности

- Поддержка больших документов с автоматическим суммированием.
- Цветной вывод через `rich`.
- Быстрые ответы из кеша.
- Сохранение истории запросов.
- Поддержка подробного просмотра записи истории.
- Возможность хранить кеш и историю в JSON или SQLite.

## Примеры использования

### Работа с YouTube

```bash
max-ai run "Сделай краткий конспект этого видео https://www.youtube.com/watch?v=example"
```

### Анализ таблицы Excel

```bash
max-ai run "Выдели ключевые показатели из этой таблицы https://example.com/data.xlsx"
```

### Обработка Markdown

```bash
max-ai run "Сделай содержание для этого файла https://example.com/readme.md"
```

## Что делать, если команда не найдена

### 1. Убедитесь, что пакет установлен

```bash
cd project
pip install -e .
```

### 2. Проверьте PATH

Для Windows путь обычно выглядит так:

```powershell
%USERPROFILE%\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts
```

### 3. Запустите напрямую через Python

```bash
python -m max_ai.cli run "ваш запрос"
```

## Troubleshooting

### Проблема: `ModuleNotFoundError: No module named 'max_ai'`

Это означает, что Python не видит пакет `max_ai`.

Возможные причины:

- Вы находитесь не в корневой папке проекта.
- Вы не установили пакет в editable режиме.
- PYTHONPATH не настроен.

Решение:

```bash
cd max-ai/project
pip install -e .
python -m max_ai.cli run "ваш запрос"
```

### Проблема: `max-ai` не запускается из терминала

Проверьте, что путь к `Scripts` добавлен в переменную среды PATH. Или используйте ссылку на прямой запуск:

```bash
python -m max_ai.cli run "ваш запрос"
```

## Логирование и отладка

Для включения подробностей используйте флаг `--verbose`.

## Тесты

Запустить тесты можно так:

```bash
python -m pytest
```

Если хотите установить тестовые зависимости, добавьте их в `requirements-dev.txt` или в `setup.py`.

## Структура проекта

```
src/max_ai/
├── cli.py
├── commands/
│   ├── cache.py
│   ├── history.py
│   ├── run.py
│   └── status.py
├── constants.py
├── core/
│   ├── agent.py
│   ├── config.py
│   └── logging_config.py
├── models/
│   └── response.py
└── utils/
    ├── cache.py
    └── history.py
```

## Установка через GitHub

```bash
pip install "https://github.com/BaToN41cK/MAX-AI"
```

## Заметки

- Не храните `config/.env` в публичных репозиториях.
- Для работы нужен хотя бы `COHERE_API_KEY`.
- `MISTRAL_API_KEY` увеличивает качество, но не обязателен.

## Лицензия

MIT
