import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'web'))

from app import app, db
from sqlalchemy import text

def column_exists(conn, table_name, column_name):
    result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in result)

with app.app_context():
    with db.engine.connect() as conn:
        if not column_exists(conn, 'species', 'description'):
            print("Adding 'description' column to 'species' table...")
            conn.execute(text('ALTER TABLE species ADD COLUMN description TEXT'))
            print("Column added.")
        else:
            print("'description' column already exists in 'species' table.") 