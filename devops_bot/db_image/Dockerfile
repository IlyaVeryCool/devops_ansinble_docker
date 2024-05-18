FROM postgres:16

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=qweqwe

COPY init.sql /docker-entrypoint-initdb.d/

# Создаем необходимые директории и устанавливаем права доступа
RUN mkdir -p /etc/postgresql/  /oracle/pg_data/archive/ && \
    chown postgres:postgres /oracle/pg_data/archive/ /etc/postgresql/ 

# Конфигурируем файл postgresql.conf с использованием переменных окружения
RUN printenv && \
    echo "listen_addresses = '*'" > /etc/postgresql/postgresql.conf && \
    echo "port = 5432" >> /etc/postgresql/postgresql.conf && \
    echo "log_destination = 'stderr'" >> /etc/postgresql/postgresql.conf && \
    echo "logging_collector = on" >> /etc/postgresql/postgresql.conf && \
    echo "log_directory = '/var/log/postgresql/'" >> /etc/postgresql/postgresql.conf && \
    echo "log_filename = 'postgresql.log'" >> /etc/postgresql/postgresql.conf && \
    echo "archive_mode = on" >> /etc/postgresql/postgresql.conf && \
    echo "archive_command = 'cp %p /oracle/pg_data/archive/%f'" >> /etc/postgresql/postgresql.conf && \
    echo "max_wal_senders = 10" >> /etc/postgresql/postgresql.conf && \
    echo "wal_level = replica" >> /etc/postgresql/postgresql.conf && \
    echo "wal_log_hints = on" >> /etc/postgresql/postgresql.conf && \
    echo "log_replication_commands = on" >> /etc/postgresql/postgresql.conf

# Задаем команду по умолчанию для запуска PostgreSQL с указанным файлом конфигурации"
CMD ["postgres" , "-c", "config_file=/etc/postgresql/postgresql.conf"]
