-- создание пользователя для репликации и предоставление прав для работы
CREATE ROLE repl_user with REPLICATION LOGIN ENCRYPTED PASSWORD 'qweqwe';
CREATE USER ADMpetr WITH PASSWORD 'eve@123';

-- создание датабазы для бота
CREATE DATABASE my_database;
\c my_database;

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone_numbers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL
);
-- добавление пользователя для общения с ботом
GRANT SELECT, INSERT ON emails TO admpetr;
GRANT SELECT, INSERT ON phone_numbers TO admpetr;
GRANT USAGE, SELECT ON SEQUENCE phone_numbers_id_seq TO admpetr;
GRANT USAGE, SELECT ON SEQUENCE emails_id_seq TO admpetr;
-- создаем физический слот репликации, по другому нормально репликация не проходила
SELECT pg_create_physical_replication_slot('replication_slot');
-- изменяем конфигурацию hba, раз только можно через sql
CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication repl_user 0.0.0.0/0 scram-sha-256');
INSERT INTO hba (lines) VALUES ('host my_database admpetr 0.0.0.0/0 scram-sha-256');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();
