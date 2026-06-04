#!/bin/bash
# Установочный скрипт для MAX-AI.
# Этот скрипт устанавливает проект и добавляет путь к max-ai в PATH.

echo "Установка MAX-AI..."
pip install max-ai

# Получение пути к каталогу bin
pythonBinPath="$HOME/.local/bin"

# Проверка существования каталога bin
if [ ! -d "$pythonBinPath" ]; then
    echo "Каталог bin не найден. Попытка найти альтернативный путь..."
    pythonBinPath=$(dirname $(which python))
    if [ ! -d "$pythonBinPath" ]; then
        echo "Не удалось найти каталог bin. Пожалуйста, добавьте его в PATH вручную."
        exit 1
    fi
fi

# Добавление пути в PATH
if [[ ":$PATH:" != *":$pythonBinPath:"* ]]; then
    echo "export PATH=\"$pythonBinPath:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc
    echo "PATH обновлен. Пожалуйста, перезапустите терминал."
else
    echo "PATH уже содержит необходимый путь."
fi

# Проверка установки
echo "Проверка установки..."
max-ai --help

echo "Установка завершена!"