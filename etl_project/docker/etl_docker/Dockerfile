FROM python:3.9.7
 
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

# This is a special case. We need to run this script as an entry point:
COPY ./docker/etl/entrypoint.sh /entrypoint.sh

# Setting up proper permissions:
RUN chmod +x '/entrypoint.sh' \
  && groupadd -r web && useradd -d /code -r -g web web \
  && chown web:web -R /code

RUN chown -R app:app $APP_HOME

COPY . .

# Running as non-root user:
USER web


