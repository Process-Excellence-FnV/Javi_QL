"""
SafeSQL AI Enterprise - Real Database Backend
Connects to PostgreSQL, MySQL, SQLite with real-time schema & query execution
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlalchemy as sa
from sqlalchemy import inspect, text, create_engine
from sqlalchemy.pool import NullPool
import json
from datetime import datetime

app = FastAPI(title="SafeSQL Backend")

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


class ConnectionConfig(BaseModel):
    connection_string: str
    driver: str = "postgresql"  # postgresql, mysql, sqlite


class QueryRequest(BaseModel):
    query: str
    fetch_results: bool = True


class TestConnectionRequest(BaseModel):
    connection_string: str


@app.post("/api/test-connection")
async def test_connection(req: TestConnectionRequest):
    """Test if database connection string is valid"""
    try:
        conn_str = req.connection_string.lower()
        connection_string = req.connection_string

        # For PostgreSQL, ensure SSL mode is set
        if "postgresql" in conn_str and "sslmode" not in conn_str:
            connection_string += "?sslmode=require"

        engine = create_engine(connection_string, poolclass=NullPool, echo=False)
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

        db_engine = create_engine(connection_string, poolclass=NullPool, echo=False)
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
    """Execute SQL query against database"""
    if not db_engine:
        raise HTTPException(status_code=400, detail="Not connected to database")

    try:
        with db_engine.begin() as conn:
            start_time = datetime.now()
            result = conn.execute(text(req.query))
            exec_time = (datetime.now() - start_time).total_seconds() * 1000

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
    uvicorn.run(app, host="127.0.0.1", port=8000)
