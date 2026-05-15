FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends sudo && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -s /bin/bash arcagent && \
    echo "arcagent ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/arcagent && \
    chmod 0440 /etc/sudoers.d/arcagent && \
    mkdir -p /home/arcagent/workspace && \
    chown arcagent:arcagent /home/arcagent/workspace

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

USER arcagent
ENV WORKSPACE_DIR=/home/arcagent/workspace

CMD ["python", "-m", "src.main"]
