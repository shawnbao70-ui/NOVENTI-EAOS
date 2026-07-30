"""Shared destructive reset for dedicated eaos_test databases (PHX-G418/G419)."""

from __future__ import annotations

from sqlalchemy import Connection, text

# System schemas never dropped.
_PROTECTED = frozenset(
    {
        "pg_catalog",
        "information_schema",
        "pg_toast",
        "pg_temp_1",
        "pg_toast_temp_1",
        "public",
    }
)


def reset_eaos_test_database(connection: Connection) -> None:
    """Drop all non-system schemas + alembic_version so upgrade head is clean.

    Fixtures previously only dropped ``kernel``, leaving ``purchase`` / ``crm`` /
    ``finance`` / ``inventory`` residue → DuplicateTable on re-upgrade.
    """

    names = connection.execute(
        text(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN (
                'pg_catalog', 'information_schema', 'pg_toast', 'public'
            )
            """
        )
    ).scalars().all()
    for name in names:
        if name in _PROTECTED or name.startswith("pg_"):
            continue
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{name}" CASCADE'))
    connection.execute(text("DROP TABLE IF EXISTS public.alembic_version"))
    connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
