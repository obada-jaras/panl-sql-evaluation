import mysql.connector
from config import DATABASE_CONFIG
import logging


def execute_and_fetch_query(query: str) -> str:
    """Execute a SQL statement and return the results as a string."""
    try:
        with mysql.connector.connect(**DATABASE_CONFIG) as cnx:
            cursor = cnx.cursor()
            cursor.execute(query)

            result = cursor.fetchall()

            return "\n".join(row[0] for row in result), False
    except Exception as e:
        logging.error(f"Failed to execute query: {e}")
        return 'error', True
