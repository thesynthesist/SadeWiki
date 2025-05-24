FROM python:3.12.10-bullseye

WORKDIR /github/workspace

COPY app.py /github/workspace/app.py
COPY classes.py /github/workspace/classes.py
COPY requirements.txt /github/workspace/requirements.txt
COPY styles.css /github/workspace/styles.css

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "app.py"]