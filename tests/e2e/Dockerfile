FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends systemd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . /src

RUN pip install --no-cache-dir .

CMD ["sh", "/src/tests/e2e/run.sh"]
