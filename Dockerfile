FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends sudo bash curl wget git && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -s /bin/bash arcagent && \
    usermod -aG sudo arcagent && \
    echo "arcagent ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    mkdir -p /home/arcagent/workspace && \
    chown arcagent:arcagent /home/arcagent/workspace

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

USER arcagent
ENV WORKSPACE_DIR=/home/arcagent/workspace
SHELL ["/bin/bash", "-c"]

CMD ["python", "-m", "src.main"]
