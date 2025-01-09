import psutil
import tkinter as tk
from tkinter import ttk
import sqlite3
import threading
import time


class SystemMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Мониторинг системы")
        self.geometry("400x300")
        self.resizable(False, False)

        # Создание меток для отображения данных
        self.cpu_label = ttk.Label(self, text="Загрузка ЦП: Идет сбор данных...", font=("Arial", 12))
        self.cpu_label.pack(pady=10)

        self.ram_label = ttk.Label(self, text="Использование ОЗУ: Идет сбор данных...", font=("Arial", 12))
        self.ram_label.pack(pady=10)

        self.disk_label = ttk.Label(self, text="Загрузка ПЗУ: Идет сбор данных...", font=("Arial", 12))
        self.disk_label.pack(pady=10)

        self.interval_label = ttk.Label(self, text="Интервал обновления (сек.):", font=("Arial", 10))
        self.interval_label.pack(pady=5)

        # Ввод интервала обновления
        self.interval_entry = ttk.Entry(self, font=("Arial", 10))
        self.interval_entry.insert(0, "1")  # Значение по умолчанию 1 секунда
        self.interval_entry.pack(pady=5)

        # Кнопка для обновления интервала
        self.set_interval_button = ttk.Button(self, text="Установить интервал", command=self.set_update_interval)
        self.set_interval_button.pack(pady=5)

        # Храним интервал обновления
        self.update_interval = 1000  # Интервал обновления (по умолчанию 1 секунда)

        # Кнопка "Начать запись"
        self.start_recording_button = ttk.Button(self, text="Начать запись", command=self.start_recording)
        self.start_recording_button.pack(pady=10)

        # Метка для таймера записи
        self.recording_timer_label = ttk.Label(self, text="", font=("Arial", 12))

        # Подключение к базе данных SQLite
        self.conn = sqlite3.connect("system_stats.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Создание таблицы, если она не существует
        self.create_table()

        # Переменные для записи
        self.recording = False
        self.recording_start_time = None  # Время начала записи

        # Запуск обновления статистики
        self.update_stats()

    def create_table(self):
        """Создание таблицы в базе данных для хранения статистики."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_stats (
                timestamp TEXT,
                cpu_usage REAL,
                ram_usage REAL,
                disk_usage REAL
            )
        """)
        self.conn.commit()

    def set_update_interval(self):
        """Устанавливает новый интервал обновления."""
        try:
            interval = int(self.interval_entry.get())
            if interval < 1:
                interval = 1
            self.update_interval = interval * 1000
        except ValueError:
            self.interval_entry.delete(0, tk.END)
            self.interval_entry.insert(0, "Неверное значение")

    def start_recording(self):
        """Начинает запись данных в БД."""
        if not self.recording:
            self.recording = True
            self.recording_start_time = time.time()  # Время начала записи

            # Скрыть кнопку "Начать запись"
            self.start_recording_button.pack_forget()
            # Показать кнопку "Остановить запись"
            self.stop_recording_button = ttk.Button(self, text="Остановить запись", command=self.stop_recording)
            self.stop_recording_button.pack(pady=10)

            # Показать таймер записи
            self.recording_timer_label.pack(pady=5)

            # Запуск потока для записи в БД (чтоб программа не висла во время записи)
            threading.Thread(target=self.record_data, daemon=True).start()

            # Обновитьтаймер записи
            self.update_timer()
        else:
            self.recording = False

    def stop_recording(self):
        """Останавливает запись данных в БД."""
        self.recording = False

        # Скрываем кнопку "Остановить запись" и таймер
        self.stop_recording_button.pack_forget()
        self.recording_timer_label.pack_forget()

        # Показываем кнопку "Начать запись"
        self.start_recording_button.pack(pady=10)

    def record_data(self):
        """Записывает данные в БД по мере обновления."""
        while self.recording:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = psutil.cpu_percent(interval=0)
            ram_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent

            # Запись данных в базу
            self.cursor.execute(
                """
                    INSERT INTO system_stats (timestamp, cpu_usage, ram_usage, disk_usage)
                    VALUES (?, ?, ?, ?)
                """,
                (timestamp, cpu_usage, ram_usage, disk_usage))
            self.conn.commit()

            # Пауза перед следующим обновлением
            time.sleep(self.update_interval / 1000.0)

    def update_timer(self):
        """Обновляет таймер записи."""
        if self.recording:
            elapsed_time = int(time.time() - self.recording_start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.recording_timer_label.config(text=f"Время записи: {minutes:02}:{seconds:02}")

            # Планирование следующего обновления через 1 сек
            self.after(1000, self.update_timer)

    def update_stats(self):
        """Обновление статистики загрузки системы."""
        cpu_usage = psutil.cpu_percent(interval=0)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        # Обновление текста меток
        self.cpu_label.config(text=f"Загрузка ЦП: {cpu_usage}%")
        self.ram_label.config(text=f"Использование ОЗУ: {ram_usage}%")
        self.disk_label.config(text=f"Загрузка ПЗУ: {disk_usage}%")

        # Планирование следующего обновления с учетом установленного интервала
        self.after(self.update_interval, self.update_stats)


if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
