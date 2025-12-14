#!/usr/bin/env python
"""
Simple SQLite shell wrapper for Django database.
Usage: python db_shell.py
"""
import sqlite3
import os
from pathlib import Path

# Get the database path from Django settings
BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / 'db.sqlite3'

if not db_path.exists():
    print(f"Error: Database file not found at {db_path}")
    exit(1)

print(f"SQLite version: {sqlite3.sqlite_version}")
print(f"Database: {db_path}")
print("Type '.help' for instructions")
print("Type '.quit' or 'exit' to exit")
print("-" * 50)

# Connect to database
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row  # Enable column access by name
cursor = conn.cursor()

try:
    while True:
        try:
            command = input("sqlite> ").strip()
            
            if not command:
                continue
            
            # Handle SQLite meta-commands
            if command.startswith('.'):
                if command == '.quit' or command == '.exit':
                    break
                elif command == '.help':
                    print("""
SQLite commands:
  .help          - Show this help message
  .tables        - List all tables
  .schema [table] - Show table schema
  .quit/.exit    - Exit the shell
  .mode column   - Set output mode to column
  .headers on    - Show column headers
                    """)
                elif command == '.tables':
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                    tables = cursor.fetchall()
                    for table in tables:
                        print(table[0])
                elif command.startswith('.schema'):
                    parts = command.split()
                    if len(parts) > 1:
                        table_name = parts[1]
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                        result = cursor.fetchone()
                        if result:
                            print(result[0])
                        else:
                            print(f"Table '{table_name}' not found")
                    else:
                        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
                        schemas = cursor.fetchall()
                        for schema in schemas:
                            print(schema[0])
                            print()
                elif command == '.mode column':
                    print("Output mode set to column")
                elif command == '.headers on':
                    print("Headers enabled")
                else:
                    print(f"Unknown command: {command}. Type '.help' for help")
                continue
            
            # Execute SQL command
            cursor.execute(command)
            
            # Check if it's a SELECT query
            if command.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                if rows:
                    # Get column names
                    columns = [description[0] for description in cursor.description]
                    print(" | ".join(columns))
                    print("-" * 80)
                    for row in rows:
                        print(" | ".join(str(val) if val is not None else 'NULL' for val in row))
                    print(f"\n({len(rows)} rows)")
                else:
                    print("(0 rows)")
            else:
                # For INSERT, UPDATE, DELETE, etc.
                conn.commit()
                print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
                
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

finally:
    conn.close()
    print("\nDatabase connection closed.")
