FROM python:3.11.4-alpine3.18

ENV SOCKET_PATH=/tmp/bernard.sock
WORKDIR /app

RUN apk --no-cache add git nginx supervisor

# Install project dependencies
RUN pip3 install poetry==1.5.1
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main --no-interaction --no-ansi

# Copy project files
COPY . /app

# Configure nginx
COPY deployment/supervisord.conf /etc/supervisord/supervisord.conf
COPY deployment/nginx-base.conf /etc/nginx/nginx.conf
COPY deployment/nginx-bernard.conf /etc/nginx/http.d/bernard.conf

CMD ["supervisord", "-c", "/etc/supervisord/supervisord.conf"]
