DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

INSERT INTO products (sku, name, price) VALUES
    ('SKU-001', 'Widget A', 19.99),
    ('SKU-002', 'Widget B', 29.99),
    ('SKU-003', 'Gadget X', 49.99);
