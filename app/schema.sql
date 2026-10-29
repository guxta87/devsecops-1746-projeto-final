-- Clube Aurora - schema e dados fictícios de exemplo.
-- Todos os dados abaixo são inventados para fins didáticos.

DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('client', 'staff', 'admin')),
    full_name     TEXT    NOT NULL
);

CREATE TABLE clients (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email     TEXT NOT NULL,
    phone     TEXT NOT NULL,
    address   TEXT NOT NULL,
    vip_tier  TEXT NOT NULL CHECK (vip_tier IN ('gold', 'platinum', 'black'))
);

CREATE TABLE bookings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id   INTEGER NOT NULL REFERENCES clients (id),
    created_by  INTEGER NOT NULL REFERENCES users (id),
    service     TEXT    NOT NULL CHECK (service IN ('viagem', 'arte', 'evento')),
    destination TEXT    NOT NULL,
    starts_at   TEXT    NOT NULL,
    amount      REAL    NOT NULL CHECK (amount >= 0)
);

CREATE TABLE audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER REFERENCES users (id),
    action     TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Usuários são criados em app/db.py (as senhas precisam de hash).

INSERT INTO clients (full_name, email, phone, address, vip_tier) VALUES
    ('Helena Vasconcelos', 'helena.v@example.com',  '+55 11 90000-0001', 'Rua das Acácias, 100 - Jardim Europa, São Paulo', 'black'),
    ('Ricardo Almeida',    'ricardo.a@example.com', '+55 21 90000-0002', 'Av. Delfim Moreira, 2000 - Leblon, Rio de Janeiro', 'platinum'),
    ('Beatriz Monteiro',   'bia.m@example.com',     '+55 31 90000-0003', 'Rua dos Ipês, 45 - Lourdes, Belo Horizonte', 'gold'),
    ('Fernando Kato',      'f.kato@example.com',    '+55 41 90000-0004', 'Alameda Prudente, 77 - Batel, Curitiba', 'platinum'),
    ('Marina Duarte',      'marina.d@example.com',  '+55 51 90000-0005', 'Rua Padre Chagas, 300 - Moinhos de Vento, Porto Alegre', 'black');

