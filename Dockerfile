FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y mysql-server cron

RUN mkdir -p /var/run/mysqld && chown mysql:mysql /var/run/mysqld

COPY ./src /usr/src/app
COPY ./config /usr/src/app/config
COPY ./alembic /usr/src/app/alembic
COPY ./alembic.ini /usr/src/app/
COPY ./entrypoint.sh /usr/src/app/

ENV MYSQL_USER=admin
ENV MYSQL_PASSWORD=password
ENV MYSQL_HOST=localhost
ENV MYSQL_DB=health_prosperity

ENV ENVIRONMENT=production

RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD ["streamlit", "run", "/usr/src/app/app.py"]
