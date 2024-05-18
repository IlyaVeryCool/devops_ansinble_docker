# Используем базовый образ Python
FROM python:3.10
RUN apt-get update && apt-get install -y \
    libpq-dev
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /bot_image

# # Копируем зависимости проекта
COPY requirements.txt .

# # # Копируем файл .env внутрь контейнера
# COPY .env .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска бота при запуске контейнера
CMD ["python", "bot.py"]
