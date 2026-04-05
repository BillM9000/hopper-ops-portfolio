"""Hopper Ops — Database connection (asyncpg)"""

import asyncpg
from server.config import DATABASE_URL

pool: asyncpg.Pool | None = None


async def init_db():
    """Create connection pool and run schema."""
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)

    # Run schema.sql
    from pathlib import Path
    schema_path = Path(__file__).parent / "schema.sql"
    schema_sql = schema_path.read_text()

    async with pool.acquire() as conn:
        await conn.execute(schema_sql)


async def close_db():
    """Close connection pool."""
    global pool
    if pool:
        await pool.close()
        pool = None


async def get_pool() -> asyncpg.Pool:
    """Get the connection pool."""
    if pool is None:
        raise RuntimeError("Database not initialized")
    return pool


async def fetch(query: str, *args):
    """Fetch multiple rows."""
    p = await get_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(r) for r in rows]


async def fetchrow(query: str, *args):
    """Fetch a single row."""
    p = await get_pool()
    async with p.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def fetchval(query: str, *args):
    """Fetch a single value."""
    p = await get_pool()
    async with p.acquire() as conn:
        return await conn.fetchval(query, *args)


async def execute(query: str, *args):
    """Execute a query."""
    p = await get_pool()
    async with p.acquire() as conn:
        return await conn.execute(query, *args)
