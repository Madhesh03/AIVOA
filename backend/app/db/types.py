"""Dialect-portable column types.

Production runs on PostgreSQL (native ``UUID`` and ``ARRAY``). The test suite and
lightweight local runs use SQLite, which supports neither. These helpers render
the native Postgres types in production and fall back to portable equivalents on
SQLite so ``create_all`` and the ORM behave identically in both environments.
"""

from sqlalchemy import ARRAY, JSON, String, Uuid

# Native ``uuid` on PostgreSQL, CHAR(32) on SQLite — returns ``uuid.UUID`` objects.
GUID = Uuid(as_uuid=True)

# Real ``text[]`` on PostgreSQL, JSON-encoded list on SQLite.
StringArray = ARRAY(String).with_variant(JSON(), "sqlite")
