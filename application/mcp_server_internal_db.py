# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import sys
from mcp.server.fastmcp import FastMCP
import psycopg2
from collections import defaultdict
import os

# Database configuration
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "YOUR_RDS_ENDPOINT"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "database": os.environ.get("DB_NAME", "agentdb"),
    "user": os.environ.get("DB_USER", "dbadmin"),
    "password": os.environ.get("DB_PASSWORD", "postgres")
}

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("internal_db_mcp")

try:
    mcp = FastMCP(name="internal_db_tool")
    logger.info("internal database Postgres MCP server initialized successfully")
except Exception as e:
    logger.error(f"Error: {str(e)}")

@mcp.tool()
async def fetch_table_schema() -> dict:
    """Tool to query table and column information from the Postgres public schema.
    - Use this tool when you need table structure for automatic query generation.
    - No need to call this if you're only performing simple data queries.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("""
                           SELECT
                               c.relname AS table_name,
                               a.attname AS column_name,
                               pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                               d.description AS column_comment
                           FROM pg_catalog.pg_attribute a
                                    JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                                    JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
                                    LEFT JOIN pg_catalog.pg_description d ON a.attrelid = d.objoid AND a.attnum = d.objsubid
                           WHERE a.attnum > 0 AND NOT a.attisdropped
                             AND n.nspname = 'public'
                             AND c.relkind = 'r'
                           ORDER BY c.relname, a.attnum;
                           """)

            rows = cursor.fetchall()
            # Group by table
            tables = defaultdict(list)
            for table_name, column_name, data_type, column_comment in rows:
                tables[table_name].append({
                    "column_name": column_name,
                    "data_type": data_type,
                    "comment": column_comment
                })

            result = [{"table_name": tbl, "columns": cols} for tbl, cols in tables.items()]
            return {"message": result, "status": "success"}

    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

@mcp.tool()
async def execute_postgres_query(query: str) -> dict:
    """Tool to execute the SQL query requested by the user.
    - If the query is clearly given, just call this tool.
    - If you need to auto-generate a query, first call fetch_table_schema to check the schema if necessary, then execute."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        conn.commit()
        return {
            "message": "\n".join(str(row) for row in result),
            "status": "success"
        }
    except Exception as e:
        return {
            "message": str(e)
        }
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    mcp.run()
