FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml .

RUN python -m pip install --no-cache-dir . \
    && python -m pip install --no-cache-dir --force-reinstall "redis==8.1.0"

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

COPY . .

EXPOSE 8080

CMD ["uvicorn", "notecli.restapi:app", "--host", "0.0.0.0", "--port", "8080"]