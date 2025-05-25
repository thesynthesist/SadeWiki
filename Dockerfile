FROM python:3.12.10-bullseye

COPY app.py /app.py
COPY classes.py /classes.py
COPY requirements.txt /requirements.txt
COPY styles.css /styles.css

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "/app.py"]
