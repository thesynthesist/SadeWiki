FROM conda/miniconda3:latest

WORKDIR /home

COPY conda.conf ./conda.conf
COPY app.py ./app.py
COPY classes.py ./classes.py
COPY requirements.txt ./requirements.txt

RUN conda create --name v1 --file conda.conf

SHELL ["/bin/bash", "-c"]

RUN conda init
RUN source ~/.bashrc
RUN conda activate v1
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "app.py"]