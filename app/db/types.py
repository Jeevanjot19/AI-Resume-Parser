"""
Database-agnostic type definitions.
Provides compatible types for both PostgreSQL and SQLite.
"""

from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB as PostgreSQLJSONB, UUID as PostgreSQLUUID, ARRAY as PostgreSQLARRAY
import json

# Use JSON for SQLite, JSONB for PostgreSQL
try:
    from sqlalchemy.dialects.postgresql import JSONB
    JSONB_TYPE = JSONB
except:
    JSONB_TYPE = JSON

# JSON type that works with both PostgreSQL and SQLite
class JSONType(TypeDecorator):
    """Platform-independent JSON type."""
    impl = JSON
    cache_ok = True

# UUID type that works with both PostgreSQL and SQLite  
class UUIDType(TypeDecorator):
    """Platform-independent UUID type (stores as string in SQLite)."""
    impl = String(36)
    cache_ok = True

# Array type that works with both PostgreSQL and SQLite
class ArrayType(TypeDecorator):
    """Platform-independent Array type (stores as JSON in SQLite)."""
    impl = JSON
    cache_ok = True

# Export compatible types
JSON_TYPE = JSON  # Works in both
UUID_TYPE = PostgreSQLUUID  # Use built-in, fallback handled by driver
ARRAY_TYPE = PostgreSQLARRAY  # Use built-in, fallback handled by driver
