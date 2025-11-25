FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml README.md ./
COPY server.py ./

# Install dependencies
RUN uv venv && uv pip install --system -e .

# Expose the default port
EXPOSE 9000

# Run the MCP server with HTTP transport
CMD ["python", "server.py", "--http"]
