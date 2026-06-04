#!/usr/bin/env pwsh
<#
Установочный скрипт для MAX-AI.
Этот скрипт устанавливает проект и добавляет путь к max-ai в PATH.
#>

# Установка проекта
Write-Host "Установка MAX-AI..."
pip install max-ai

# Получение пути к каталогу Scripts
$pythonScriptsPath = "$env:USERPROFILE\AppData\Local\Programs\Python\Python313\Scripts"

# Проверка существования каталога Scripts
if (-not (Test-Path $pythonScriptsPath)) {
    Write-Host "Каталог Scripts не найден. Попытка найти альтернативный путь..."
    $pythonScriptsPath = (Get-Command python).Source -replace "python.exe", "Scripts"
    if (-not (Test-Path $pythonScriptsPath)) {
        Write-Host "Не удалось найти каталог Scripts. Пожалуйста, добавьте его в PATH вручную."
        exit 1
    }
}

# Добавление пути в PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$pythonScriptsPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$pythonScriptsPath", "User")
    Write-Host "PATH обновлен. Пожалуйста, перезапустите терминал."
} else {
    Write-Host "PATH уже содержит необходимый путь."
}

# Проверка установки
Write-Host "Проверка установки..."
max-ai --help

Write-Host "Установка завершена!"