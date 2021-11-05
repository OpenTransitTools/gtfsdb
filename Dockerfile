FROM python:3

RUN pip install zc.buildout psycopg2-binary

WORKDIR /app
COPY . .

RUN buildout install prod postgresql

ENTRYPOINT ["bin/gtfsdb-load"]
