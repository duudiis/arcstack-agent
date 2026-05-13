FROM python:3.12-slim

RUN useradd -m -s /bin/bash arcagent && \
    mkdir -p /home/arcagent/workspace && \
    chown arcagent:arcagent /home/arcagent/workspace

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

USER arcagent
ENV WORKSPACE_DIR=/home/arcagent/workspace

CMD ["python", "-m", "src.main"]
