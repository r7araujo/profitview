import sqlite3
from pathlib import Path

DB_PATH = Path("db/data.db")
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

conn.executescript("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    investment_group TEXT NOT NULL,
    investment_subgroup TEXT NOT NULL,
    UNIQUE (investment_group, investment_subgroup)
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'BRL',
    active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    operation_date TEXT NOT NULL,
    settlement_date TEXT,
    asset_id INTEGER,
    operation_type TEXT NOT NULL CHECK (
        operation_type IN (
            'COMPRA', 'VENDA', 'APORTE', 'RETIRADA',
            'RENDIMENTO', 'DIVIDENDO', 'AMORTIZACAO',
            'TAXA', 'AJUSTE'
        )
    ),
    quantity_micros INTEGER,
    unit_price_cents INTEGER,
    gross_value_cents INTEGER NOT NULL,
    fees_cents INTEGER NOT NULL DEFAULT 0,
    broker TEXT,
    external_id TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    UNIQUE (broker, external_id)
);

CREATE TABLE IF NOT EXISTS quarterly_closings (
    id INTEGER PRIMARY KEY,
    closing_date TEXT NOT NULL UNIQUE,
    calculated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_locked INTEGER NOT NULL DEFAULT 1,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS closing_positions (
    closing_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    quantity_micros INTEGER NOT NULL,
    cost_basis_cents INTEGER NOT NULL,
    market_value_cents INTEGER,
    realized_profit_cents INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (closing_id, asset_id),
    FOREIGN KEY (closing_id) REFERENCES quarterly_closings(id),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE TABLE IF NOT EXISTS current_positions (
    asset_id INTEGER PRIMARY KEY,
    quantity_micros INTEGER NOT NULL,
    cost_basis_cents INTEGER NOT NULL,
    market_value_cents INTEGER,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(operation_date);

CREATE INDEX IF NOT EXISTS idx_transactions_asset_date
ON transactions(asset_id, operation_date);
""")

conn.close()
