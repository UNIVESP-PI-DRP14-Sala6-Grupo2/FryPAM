FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY Pipfile /app/
RUN pip install pipenv \
    && pipenv install --deploy
# Copy project
COPY . /app/

RUN pipenv run python manage.py migrate && pipenv run python manage.py createsuperuser --noinput --email admin@frypam.com --password App@frypam2025

# Expose port for the Django app
EXPOSE 8000

# Run Django development server
CMD ["pipenv", "run", "python","manage.py", "runserver", "0.0.0.0:8000"]