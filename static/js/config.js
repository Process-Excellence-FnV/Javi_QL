/**
 * Application configuration
 */

export const CONFIG = {
    API_BASE: "http://127.0.0.1:8000/api",
    TABLES_PER_PAGE: 25,
    BASE_SCHEMA_SQL: `
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'active',
            role TEXT DEFAULT 'User',
            last_login DATETIME
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(10, 2),
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        INSERT OR IGNORE INTO users (id, name, email, status, role, last_login) VALUES
            (1, 'John Doe', 'john@example.com', 'active', 'Admin', CURRENT_TIMESTAMP),
            (2, 'Jane Smith', 'jane@example.com', 'active', 'User', CURRENT_TIMESTAMP);

        INSERT OR IGNORE INTO orders (id, user_id, amount, status, created_at) VALUES
            (1, 1, 150.00, 'completed', CURRENT_TIMESTAMP),
            (2, 2, 75.50, 'pending', CURRENT_TIMESTAMP);
    `
};

export const STATE = {
    db: null,
    backupVault: [],
    totalProtectedRows: 0,
    activeRollbackSql: "",
    isRealDatabase: false,
    currentSchema: {},
    currentWorkingTable: null,
    tableUsageStats: {},
    inspectorCurrentPage: 1
};
