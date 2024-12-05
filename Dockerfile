FROM python:3.10

# Создаем директорию для проекта
RUN mkdir /src

# Копируем файл зависимостей
COPY requirements.txt /src

# Обновляем список пакетов и устанавливаем необходимые библиотеки
RUN apt-get install -y g++

# Устанавливаем зависимости Python
RUN pip3 install -r /src/requirements.txt --no-cache-dir

# Копируем исходный код
COPY src/ /src
COPY uwsgi.ini /src

# Устанавливаем рабочую директорию
WORKDIR /src

# Запускаем приложение
CMD ["uwsgi", "--ini", "uwsgi.ini"]
