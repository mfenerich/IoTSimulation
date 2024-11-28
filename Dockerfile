FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire application (including migrations and Alembic config)
COPY ./app ./app

# Copy the entrypoint script
COPY ./app/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the application port
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
