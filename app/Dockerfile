FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
COPY data/ data/

RUN python3 -m pip install pip --upgrade && pip3 install -r requirements.txt

COPY main.py main.py

CMD ["streamlit", "run", "main.py"]

EXPOSE 8051
