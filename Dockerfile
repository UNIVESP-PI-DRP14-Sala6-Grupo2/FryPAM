FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY Pipfile /app/
RUN pip install pipenv && pipenv requirements > requirements.txt && pip install -r requirements.txt
# Copy project
COPY . /app/

# Expose port for the Django app
EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]