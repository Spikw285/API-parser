import requests
import schedule
import time
from datetime import datetime, timedelta
import json
import signal
import sys

# API настройки
url = "https://stage.uchet24.kz/api/v1/greenkassa/get-checks-bin/"
bin_value = "821023402309"

# Начальные временные данные
start_time = datetime.strptime("2024-08-06T07:00:00", "%Y-%m-%dT%H:%M:%S")
end_time_limit = datetime.strptime("2024-08-06T23:59:59", "%Y-%m-%dT%H:%M:%S")

# Список для хранения результатов
results = []

# Отправка запроса
def send_request():
    global start_time

    # Конец текущего интервала
    end_time = start_time + timedelta(hours=6) - timedelta(seconds=1)
    if end_time > end_time_limit:
        end_time = end_time_limit

    # Формируем данные для POST-запроса
    data = {
        "start_date": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_date": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "bin": bin_value
    }

    try:
        # Отправка POST-запроса
        response = requests.post(url, json=data)
        print(f"Запрос отправлен: {data}")
        print(f"Ответ сервера: {response.status_code} - {response.text}")

        # Сохраняем запрос и ответ
        results.append({
            "request": data,
            "response": {
                "status_code": response.status_code,
                "body": response.text
            }
        })

    except Exception as e:
        print(f"Ошибка при отправке запроса: {e}")

    # Сдвигаем start_time на конец текущего интервала + 1 секунда
    start_time = end_time + timedelta(seconds=1)

    # Если достигли конца дня, завершаем
    if start_time > end_time_limit:
        print("Конец дня достигнут. Сохраняем данные и завершаем выполнение.")
        save_results_to_file()
        schedule.clear()

# Сохранение данных в файл
def save_results_to_file():
    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    print("Данные сохранены в файл results.json")

# Завершение по сигналу CTRL+C
def stop_script(signal_received, frame):
    print("\nСкрипт остановлен пользователем. Сохраняем данные...")
    save_results_to_file()
    sys.exit(0)

signal.signal(signal.SIGINT, stop_script)

# Планирование задачи
schedule.every(10).minutes.do(send_request)
send_request()  # Выполняем первый запрос сразу

# Основной цикл
while True:
    schedule.run_pending()
    time.sleep(1)
