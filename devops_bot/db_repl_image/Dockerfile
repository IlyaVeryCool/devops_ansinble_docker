FROM postgres:16

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=qweqwe

# Создаем необходимые директории и устанавливаем права доступа
RUN mkdir -p /etc/postgresql/ && \
    chmod 750 /var/lib/postgresql/data

# Конфигурируем файл postgresql.conf с использованием переменных окружения
CMD echo "listen_addresses = '*'" > /etc/postgresql/postgresql.conf && \
    echo "port = 5432" >> /etc/postgresql/postgresql.conf


# Устанавливаем точку входа для инициализации реплики и запуска PostgreSQL
ENTRYPOINT [ "bash", "-c", "\
set -e && \
rm -rf /var/lib/postgresql/data/* && \
sleep 10 && \
echo ${DB_REPL_PASSWORD} | pg_basebackup -v -R \
-h ${DB_HOST} -p ${DB_PORT} -U ${DB_REPL_USER} -W -P \
-D /var/lib/postgresql/data && \
exec docker-entrypoint.sh $@"]

# Задаем команду по умолчанию для запуска PostgreSQL с указанным файлом конфигурации
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
