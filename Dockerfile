# Dockerfile

FROM python:3.9-slim AS build-stage

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

ARG CACHEBUST=1
RUN git clone https://github.com/ArmandoDLaRosa/health-prosperity-index.git .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim

COPY --from=build-stage /usr/src/app /usr/src/app
COPY --from=build-stage /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=build-stage /usr/local/bin/ /usr/local/bin/

RUN apt-get update && apt-get install -y \
    cron \
    mariadb-server \
    mariadb-client \
    && rm -rf /var/lib/apt/lists/*

# Create a custom MySQL configuration file
RUN echo "[mysqld]\nbind-address = 0.0.0.0" > /etc/mysql/my.cnf

RUN mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld

ENV MYSQL_USER=admin
ENV MYSQL_PASSWORD=password
ENV MYSQL_HOST=localhost
ENV MYSQL_DB=world_indexes
ENV MYSQL_ROOT_PASSWORD=root_password
ENV ENVIRONMENT=production

RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE 8501
EXPOSE 3306

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD ["streamlit", "run", "src/app.py"]
