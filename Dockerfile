FROM python:3.10.5

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD python ./src/serve/server.py

EXPOSE 5000