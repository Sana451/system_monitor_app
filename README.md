# Системный монитор

Простое приложение на Python для мониторинга использования системы (ЦП, ОЗУ, диск) с возможностью записи данных в базу данных SQLite.

## Возможности
- Живой мониторинг использования ЦП, ОЗУ и диска.
- Настраиваемый интервал обновления.
- Запись данных в базу данных SQLite.
- Удобный интерфейс с использованием Tkinter.

## Установка
1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/YOUR_USERNAME/system-monitor.git
    cd system-monitor
    ```

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. Запустите приложение:
    ```bash
    python main.py
    ```

## Использование
- Нажмите **«Начать запись»**, чтобы начать запись статистики системы в базу данных SQLite.
- Настройте интервал обновления, используя поле ввода, и нажмите **«Установить интервал»**.
- Нажмите **«Остановить запись»**, чтобы остановить запись.

## Требования
- Python версии 3.8 или выше
- Библиотеки:
  - psutil
  - tkinter (встроена в Python)