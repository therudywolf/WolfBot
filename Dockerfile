# Используем официальный образ Python в качестве базового
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .

# Устанавливаем все Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем сам скрипт и файл с шутками в контейнер
COPY wolfbot.py .
COPY jokes.txt .

# Устанавливаем команду для запуска скрипта
CMD ["python", "wolfbot.py"]

# Указываем, что контейнер будет слушать порт 80 (если нужно для общения через API)
EXPOSE 80