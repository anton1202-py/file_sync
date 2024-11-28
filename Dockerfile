FROM python:3.12-slim

RUN mkdir /src

COPY requirements.txt /src

RUN pip3 install -r /src/requirements.txt --no-cache-dir


COPY src/ /src


WORKDIR /src

CMD ["python3", "app.py"]