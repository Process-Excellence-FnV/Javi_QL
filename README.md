# Javi.QL - Just in time Automated Versioned Intelligence

**A powerful SQL query console with real-time database connectivity, automatic backup management, and comprehensive audit logging.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## 🎯 Overview

Javi.QL is a browser-based SQL query execution engine with enterprise-grade safety features. Execute queries against PostgreSQL, MySQL, or SQLite databases with automatic pre-mutation CSV backups, intelligent rollback capability, real-time schema inspection, and complete audit trails.

**Key Innovation**: Never lose data again. Every DELETE or UPDATE automatically backs up affected rows as CSV files before execution, with one-click rollback generation.

## ✨ Features

### 🔍 Query Console
- **Real-time SQL execution** against PostgreSQL, MySQL, and SQLite
- **Syntax formatting** and dry-run safety checks with EXPLAIN plans
- **Keyboard shortcuts**: `Ctrl+Enter` to execute queries
- **Auto-syntax highlighting** with code beautification

### 💾 Smart Backup Vault
- **Automatic pre-mutation backups** for DELETE and UPDATE operations
- **CSV auto-download** on query execution
- **One-click rollback** SQL generation from backed-up rows
- **Audit trail** with timestamps, affected row counts, and execution times
- **Backup history** with unlimited restore capability

### 📊 Live Database Inspector
- **Real-time schema browser** showing all tables and columns
- **Type information** for every column
- **Pagination support** for databases with 500+ tables
- **Quick-select queries** from schema context menu

### 🔐 Audit & Compliance
- **Query logging** to PostgreSQL (`Javi_QL_logs` table)
- **Audit event logging** for all mutations (`Javi_QL_audit_logs` table)
- **Per-user tracking** with email-based session management
- **Execution metrics** (execution time, row counts, status)

### 🎨 Modern UI
- **Dark mode interface** with glassmorphism design
- **Real-time loading indicators** during operations
- **Responsive design** supporting desktop and tablet
- **Tab-based navigation** (Query Console, Inspector, Vault)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- A modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/janhavichauhanint-art/JaviIQ.git
   cd JaviIQ
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create a `.env` file in the project root:
   ```bash
   # Database Configuration (for audit logs)
   DB_TYPE=postgresql
   DB_HOST=your-postgres-host.com
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   
   # FastAPI Configuration
   API_HOST=127.0.0.1
   API_PORT=8000
   
   # Query Logs Table
   LOGS_TABLE=Javi_QL_logs
   ```

4. **Start the backend**
   ```bash
   python main.py
   ```
   
   The server will start on `http://127.0.0.1:8000`

5. **Open in browser**
   - Open `index.html` directly in your browser, or
   - Serve it via a local server:
     ```bash
     # Using Python's built-in server
     python -m http.server 8001
     # Then navigate to http://localhost:8001
     ```

## 📖 Usage Guide

### Connecting to a Database

1. Click the **"No Database Connected"** button in the top-left
2. Select your database type (PostgreSQL, MySQL, or SQLite)
3. Enter connection details:
   - **Host**: Database server address
   - **Port**: Database port (5432 for PostgreSQL, 3306 for MySQL)
   - **Database**: Database name
   - **Username**: Database user
   - **Password**: Database password
4. Click **"Test Connection"** to validate
5. Click **"Save Config"** to connect

### Executing Queries

1. Type your SQL query in the **Query Console** tab
2. Press `Ctrl+Enter` or click **"Run Query"**
3. View results in the **Execution Results** panel
4. For UPDATE/DELETE queries, CSV backups auto-download automatically

### Using the Vault & Rollback

1. Navigate to the **"Vault & Backups"** tab
2. View all backup events with timestamps and row counts
3. Click **"Rollback"** on any backup to:
   - View the pre-mutation data
   - Copy rollback SQL to clipboard
   - Download as SQL file
   - Execute rollback directly

### Live Database Inspector

1. Open the **"Live Inspector"** tab
2. Browse all tables and their columns
3. Click **"Query"** to auto-populate the query editor
4. Click **"Delete"** to drop a table (with automatic backup)

### Query History & Audit

1. Click your email in the top-right to view:
   - All executed queries
   - Execution timestamps
   - Execution times (ms)
   - Query types (SELECT, UPDATE, DELETE, etc.)

## 🏗️ Project Structure

```
JaviIQ/
├── index.html              # Main frontend application (vanilla JS + Tailwind CSS)
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (not in git)
├── .gitignore              # Git ignore rules
├── static/
│   └── js/
│       ├── api.js          # API client functions
│       ├── connection.js   # Database connection UI
│       ├── database.js     # Database operations
│       ├── backup.js       # Backup/restore logic
│       ├── query.js        # Query execution
│       ├── ui.js           # UI rendering utilities
│       ├── config.js       # Global configuration
│       ├── helpers.js      # Helper functions
│       └── app.js          # Main app initialization
└── README.md               # This file
```

## 🔧 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **psycopg2**: PostgreSQL adapter
- **PyMySQL**: MySQL adapter
- **Pydantic**: Data validation
- **python-dotenv**: Environment configuration

### Frontend
- **Vanilla JavaScript** (ES modules)
- **Tailwind CSS**: Utility-first CSS framework
- **FontAwesome**: Icon library
- **SQL.js**: WASM SQLite engine (fallback)

## 🔐 Security Features

- **Connection pooling** with SSL/TLS support for cloud databases
- **SASL authentication** for secure connections
- **Environment-based credentials** (credentials never in source code)
- **Pre-execution backup** prevents data loss from mistakes
- **Audit logging** for compliance and troubleshooting
- **Session-based user tracking** with email identification
- **Query history** for accountability

## 📊 Database Support

| Database | Support | SSL/TLS | Notes |
|----------|---------|---------|-------|
| PostgreSQL | ✅ Full | ✅ Yes | Recommended; supports Cosmos DB |
| MySQL | ✅ Full | ✅ Yes | Compatible with MariaDB |
| SQLite | ✅ Full | ⚠️ No | File-based; no SSL needed |

## 🚨 Important Notes

### Environment Variables
The `.env` file is **not tracked in git** (see `.gitignore`). You must create it locally with your own database credentials.

### Logging Database
For full audit logging capabilities, you need a PostgreSQL database where logs tables will be created automatically on first run.

### Connection Pooling
The application uses connection pooling to optimize performance:
- Pool size: 5 connections
- Max overflow: 10 additional connections
- Connection recycle: 3600 seconds (1 hour)
- Connection timeout: 10 seconds

## 🐛 Troubleshooting

### Connection Failed: SASL authentication failed
**Solution**: Verify your database credentials in `.env`. For Azure PostgreSQL Cosmos, use `username@servername` format.

### Database Connection Timeout
**Solution**: Check firewall rules and network connectivity. Increase `connect_timeout` in `main.py` if needed.

### CSV not auto-downloading
**Solution**: Check browser download settings. Ensure auto-download is enabled in the Settings tab.

### Backend not responding
**Solution**: Verify backend is running (`python main.py`) and listening on `127.0.0.1:8000`.

## 📈 Performance Tips

1. **Use indexes** on frequently queried columns
2. **Limit result sets** for large tables (add `LIMIT` clauses)
3. **Use the Inspector** pagination for databases with many tables
4. **Archive old audit logs** periodically to maintain performance

## 📝 License

MIT License - feel free to use and modify for your needs.

## 👨‍💻 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for safer SQL execution**
