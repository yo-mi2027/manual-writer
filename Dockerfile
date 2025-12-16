# vault-writer MCP Server
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Default vault path (can be overridden via volume mount)
RUN mkdir -p /app/vault

# Environment variable for vault path (override in config.yaml or via env)
ENV VAULT_WRITER_VAULT_PATH=/app/vault

# Expose port for HTTP mode (if using fastmcp with --port)
EXPOSE 8000

# Default: run in stdio mode (for MCP client integration)
# Override CMD to use HTTP mode: ["fastmcp", "run", "src/vault_writer_server.py", "--port", "8000"]
CMD ["python", "src/vault_writer_server.py"]
