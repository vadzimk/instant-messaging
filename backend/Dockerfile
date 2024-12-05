# Base stage
FROM python:3.10-slim AS base
WORKDIR /usr/src/app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN apt-get update &&\
    apt-get install -y --no-install-recommends gcc libffi-dev g++ postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Dependencies stage
FROM base AS dependencies
COPY ./Pipfile ./Pipfile.lock ./
RUN pip install --no-cache-dir pipenv

# installs dependecies in .venv
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy --ignore-pipfile # for production

# Final stage
FROM base AS final
COPY --from=dependencies /usr/src/app/.venv/ /usr/src/app/.venv/
# Set the PATH to include the virtualenv's bin
ENV PATH="/usr/src/app/.venv/bin:$PATH"

# set default username
ARG APP_USER_NAME=appuser
# Create a non-root user and group
RUN groupadd -r "$APP_USER_NAME" \
    && useradd -r -g "$APP_USER_NAME" -m "$APP_USER_NAME" \
    && chown -R "$APP_USER_NAME" /usr/src/app \

COPY ./ ./
RUN rm -rf tests # for production

RUN chmod +x wait-for-postgres.sh docker-entrypoint.sh
EXPOSE 8000

# Switch to the non-root user
USER "$APP_USER_NAME"

ENV ENV=production

# for debugging only
#CMD ["tail", "-f", "/dev/null"]
ENTRYPOINT ["./docker-entrypoint.sh"]

