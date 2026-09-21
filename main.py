"""
Javi.QL - Just in time Automated Versioned Intelligence
Real Database Backend - Connects to PostgreSQL, MySQL, SQLite with real-time schema & query execution
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlalchemy as sa
from sqlalchemy import inspect, text, create_engine
from sqlalchemy.pool import QueuePool
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Javi.QL Backend")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database connection
db_engine = None
db_connection_string = None

# PostgreSQL connection for query logs (from .env)
DB_USER = os.getenv("DB_USER", "citus")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test@213").replace("@", "%40")
DB_HOST = os.getenv("DB_HOST", "c-picking-blr1.soecbxqsdjgd4v.postgres.cosmos.azure.com")
DB_PORT = os.getenv("DB_PORT", "6432")
DB_NAME = os.getenv("DB_NAME", "citus1")
POSTGRES_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&options=-csearch_path%3Dpublic"
logs_engine = None

def init_logs_db():
    """Initialize PostgreSQL connection and create logs tables"""
    global logs_engine
    try:
        logs_engine = create_engine(
            POSTGRES_URL,
            poolclass=QueuePool,
            pool_size=3,
            max_overflow=5,
            pool_recycle=3600,
            connect_args={
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "sslmode": "require",
                "client_encoding": "UTF8"
            }
        )
        with logs_engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS Javi_QL_logs (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255),
                    query TEXT,
                    query_type VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time FLOAT,
                    status VARCHAR(20) DEFAULT 'success'
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS Javi_QL_audit_logs (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255),
                    action VARCHAR(100),
                    table_name VARCHAR(100),
                    rows_count INTEGER,
                    query TEXT,
                    query_type VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_time FLOAT,
                    csv_filename VARCHAR(255)
                )
            """))
            conn.commit()
        print("[OK] Javi_QL_logs and Javi_QL_audit_logs tables initialized")
    except Exception as e:
        print(f"[WARNING] Could not initialize logs DB: {str(e)}")

def log_query_to_db(email, query, query_type, exec_time):
    """Store query log in PostgreSQL"""
    try:
        if logs_engine:
            with logs_engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Javi_QL_logs (email, query, query_type, execution_time)
                    VALUES (:email, :query, :query_type, :exec_time)
                """), {
                    "email": email,
                    "query": query[:500],
                    "query_type": query_type,
                    "exec_time": exec_time
                })
                conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log query: {str(e)}")

def log_audit_event(email, action, table_name, rows_count, query, query_type, exec_time, csv_filename=None):
    """Store audit log (backup/restore events) in PostgreSQL"""
    try:
        if logs_engine:
            with logs_engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO Javi_QL_audit_logs (email, action, table_name, rows_count, query, query_type, execution_time, csv_filename)
                    VALUES (:email, :action, :table_name, :rows_count, :query, :query_type, :exec_time, :csv_filename)
                """), {
                    "email": email,
                    "action": action,
                    "table_name": table_name,
                    "rows_count": rows_count,
                    "query": query[:500] if query else None,
                    "query_type": query_type,
                    "exec_time": exec_time,
                    "csv_filename": csv_filename
                })
                conn.commit()
    except Exception as e:
        print(f"[WARNING] Could not log audit event: {str(e)}")


class ConnectionConfig(BaseModel):
    connection_string: str
    driver: str = "postgresql"  # postgresql, mysql, sqlite


class QueryRequest(BaseModel):
    query: str
    fetch_results: bool = True
    email: str = "anonymous"


class TestConnectionRequest(BaseModel):
    connection_string: str


class QueryLogRequest(BaseModel):
    email: str
    query: str
    fetch_results: bool = True


# Store user sessions and query logs in memory (simple approach)
user_sessions = {}
query_logs = {}  # {email: [{"query": "...", "timestamp": "...", "type": "..."}]}


@app.post("/api/whoami")
async def whoami(req: QueryLogRequest):
    """Get current user info and return email"""
    email = req.email.strip().lower()
    user_sessions[email] = datetime.now().isoformat()

    if email not in query_logs:
        query_logs[email] = []

    return {
        "email": email,
        "status": "authenticated",
        "last_seen": user_sessions[email],
        "total_queries": len(query_logs.get(email, []))
    }


@app.get("/api/query-history/{email}")
async def get_query_history(email: str):
    """Get query history for a user from PostgreSQL"""
    email = email.strip().lower()
    try:
        if logs_engine:
            with logs_engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT query, query_type, timestamp, execution_time
                    FROM Javi_QL_logs
                    WHERE email = :email
                    ORDER BY timestamp DESC
                    LIMIT 100
                """), {"email": email})

                queries = []
                for row in result:
                    queries.append({
                        "query": row[0],
                        "type": row[1],
                        "timestamp": row[2].isoformat() if row[2] else None,
                        "exec_time": row[3]
                    })

                return {
                    "email": email,
                    "queries": queries
                }
    except Exception as e:
        print(f"Error fetching history: {str(e)}")

    return {
        "email": email,
        "queries": []
    }


@app.post("/api/test-connection")
async def test_connection(req: TestConnectionRequest):
    """Test if database connection string is valid"""
    try:
        conn_str = req.connection_string.lower()
        connection_string = req.connection_string

        # For PostgreSQL, ensure SSL mode is set
        if "postgresql" in conn_str and "sslmode" not in conn_str:
            connection_string += "?sslmode=require"

        engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            connect_args={
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "sslmode": "require",
                "client_encoding": "UTF8"
            },
            echo=False
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "success": True,
            "message": "Connection successful!",
            "driver": "postgresql" if "postgresql" in conn_str else "mysql" if "mysql" in conn_str else "sqlite"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@app.post("/api/connect")
async def connect_database(req: ConnectionConfig):
    """Establish database connection"""
    global db_engine, db_connection_string

    try:
        connection_string = req.connection_string

        # For PostgreSQL, ensure SSL mode is set
        if "postgresql" in connection_string.lower() and "sslmode" not in connection_string.lower():
            connection_string += "?sslmode=require"

        db_engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            connect_args={
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "sslmode": "require",
                "client_encoding": "UTF8"
            },
            echo=False
        )
        db_connection_string = connection_string

        # Test connection
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "success": True,
            "message": "Connected to database",
            "driver": req.driver
        }
    except Exception as e:
        db_engine = None
        raise HTTPException(status_code=400, detail=f"Failed to connect: {str(e)}")


@app.get("/api/schema")
async def get_schema():
    """Fetch complete database schema"""
    if not db_engine:
        raise HTTPException(status_code=400, detail="Not connected to database")

    try:
        schema = {}

        # Use direct SQL for PostgreSQL to avoid PgBouncer hangs
        if db_connection_string and "postgresql" in db_connection_string.lower():
            with db_engine.connect() as conn:
                # Get tables from information_schema
                tables_query = text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables_result = conn.execute(tables_query).fetchall()
                tables = [row[0] for row in tables_result]

                # Get columns for each table
                for table_name in tables:
                    try:
                        columns_query = text(f"""
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns
                            WHERE table_schema = 'public' AND table_name = '{table_name}'
                            ORDER BY ordinal_position
                        """)
                        columns_result = conn.execute(columns_query).fetchall()

                        schema[table_name] = {
                            "columns": [
                                {
                                    "name": col[0],
                                    "type": col[1],
                                    "nullable": col[2] == 'YES'
                                }
                                for col in columns_result
                            ]
                        }
                    except Exception as e:
                        print(f"Error loading columns for {table_name}: {str(e)}")
                        continue
        else:
            # For MySQL/SQLite, use inspector
            inspector = inspect(db_engine)
            tables = inspector.get_table_names()

            for table_name in tables:
                try:
                    columns = inspector.get_columns(table_name)
                    schema[table_name] = {
                        "columns": [
                            {
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col.get("nullable", True)
                            }
                            for col in columns
                        ]
                    }
                except Exception as e:
                    print(f"Error loading table {table_name}: {str(e)}")
                    continue

        return {
            "tables": list(schema.keys()),
            "schema": schema,
            "count": len(schema)
        }
    except Exception as e:
        print(f"Schema fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Schema fetch failed: {str(e)}")


@app.post("/api/execute-query")
async def execute_query(req: QueryRequest):
    """Execute SQL query against database and log it"""
    if not db_engine:
        raise HTTPException(status_code=400, detail="Not connected to database")

    email = req.email.strip().lower()
    query_type = req.query.strip().split()[0].upper()
    timestamp = datetime.now().isoformat()

    try:
        with db_engine.begin() as conn:
            start_time = datetime.now()
            result = conn.execute(text(req.query))
            exec_time = (datetime.now() - start_time).total_seconds() * 1000

            # Log the query to PostgreSQL
            log_query_to_db(email, req.query, query_type, round(exec_time, 2))

            # For SELECT queries, fetch results
            if req.fetch_results and result.returns_rows:
                rows = result.fetchall()
                columns = result.keys()

                return {
                    "success": True,
                    "type": "SELECT",
                    "columns": list(columns),
                    "rows": [dict(row._mapping) for row in rows],
                    "row_count": len(rows),
                    "exec_time": round(exec_time, 2)
                }
            else:
                # For INSERT/UPDATE/DELETE - auto-commits with db_engine.begin()
                affected = result.rowcount
                return {
                    "success": True,
                    "type": "MODIFY",
                    "affected_rows": affected,
                    "exec_time": round(exec_time, 2)
                }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")


@app.post("/api/get-table-data")
async def get_table_data(req: QueryRequest):
    """Fetch all data from a specific table"""
    if not db_engine:
        raise HTTPException(status_code=400, detail="Not connected to database")

    try:
        with db_engine.connect() as conn:
            result = conn.execute(text(req.query))
            rows = result.fetchall()
            columns = result.keys()

            return {
                "success": True,
                "columns": list(columns),
                "rows": [dict(row._mapping) for row in rows],
                "row_count": len(rows)
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch table data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("[INIT] Initializing Javi_QL logging system...")
    init_logs_db()
    print("[OK] Backend ready!")
    uvicorn.run(app, host="127.0.0.1", port=8000)
