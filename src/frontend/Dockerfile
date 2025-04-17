FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 9000

ENTRYPOINT ["streamlit","run","--server.port","9000"]

CMD ["app.py"]