FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
# COPY ./docker-entrypoint.sh /app/docker-entrypoint.sh
# RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]
# ENTRYPOINT ["sh","/app/docker-entrypoint.sh"]

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]