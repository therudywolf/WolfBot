# WolfBot Discord Bot - Docker Image
# License: GNU Affero General Public License v3 (AGPLv3)
# Author: therudywolf

FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Create data directory for database files
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# Copy dependencies file and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY wolfbot.py .
COPY web_dashboard.py .
COPY jokes.txt .
COPY LICENSE .

# Create non-root user for security (optional but recommended)
# RUN useradd -m -u 1000 wolfbot && chown -R wolfbot:wolfbot /app
# USER wolfbot

# Health check to monitor bot status
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('/app/data/bot_database.db')" || exit 1

# Environment variables (can be overridden)
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/bot_database.db

# Run the bot
CMD ["python", "wolfbot.py"]

# Expose port for web dashboard (optional)
EXPOSE 5000
