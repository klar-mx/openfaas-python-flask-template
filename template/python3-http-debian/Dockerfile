FROM --platform=${TARGETPLATFORM:-linux/amd64} ghcr.io/openfaas/of-watchdog:0.9.10 as watchdog
FROM --platform=${TARGETPLATFORM:-linux/amd64} python:3.11-slim-bullseye as build
MAINTAINER Klar Devops <devops@klar.mx>

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ARG ADDITIONAL_PACKAGE
# Alternatively use ADD https:// (which will not be cached by Docker builder)

RUN apt-get -qy update \
    && apt-get -qy install ${ADDITIONAL_PACKAGE} \
    && rm -rf /var/lib/apt/lists/*

# Add non root user
RUN addgroup --system app && adduser app --system --ingroup app
RUN chown app /home/app

USER app

ENV PATH=$PATH:/home/app/.local/bin

WORKDIR /home/app/

COPY --chown=app:app index.py           .
COPY --chown=app:app requirements.txt   .

USER root
ARG PIP_ROOT_USER_ACTION=ignore
RUN --mount=type=secret,id=pipconf,mode=0666,dst=/root/.config/pip/pip.conf \
        pip install --upgrade pip && \
        pip install --no-warn-script-location virtualenv poetry pipenv
RUN --mount=type=secret,id=pipconf,mode=0666,dst=/root/.config/pip/pip.conf \
        pip install --no-cache-dir -r requirements.txt

# Build the function directory and install any user-specified components
USER app

RUN mkdir -p function
RUN touch ./function/__init__.py
WORKDIR /home/app/function/
COPY --chown=app:app function/requirements.txt	.
RUN --mount=type=secret,id=pipconf,mode=0666,dst=/home/app/.config/pip/pip.conf \
        pip install --no-cache-dir --user -r requirements.txt

# Install function code
USER root
#COPY --chown=app:app function/   .
RUN chown -R app:app /home/app

USER app

FROM build as test
ARG TEST_COMMAND=tox
ARG TEST_ENABLED=true
RUN [ "$TEST_ENABLED" = "false" ] && echo "skipping tests" || eval "$TEST_COMMAND"

FROM build as ship
WORKDIR /home/app/

# Configure WSGI server and healthcheck
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1

# set up of-watchdog for HTTP mode
ENV fprocess="python index.py"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:5000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
