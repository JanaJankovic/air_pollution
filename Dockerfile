FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD python ./src/serve/server.py

EXPOSE 5000