from datetime import datetime as dt

import asyncpgsa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime, Numeric
)
from sqlalchemy.sql import select

from ylab_app.calculate import currency_conversion
from ylab_app.security import generate_password_hash

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String(100), nullable=False, unique=True),
    Column('password_hash', String(128), nullable=False),
    Column('balance', Numeric(14, 2), nullable=False, default=0.00),
    Column('currency', String(3), ForeignKey('currencies.id', ondelete='CASCADE'))
)

transactions = Table(
    'transactions', metadata,
    Column('id', Integer, primary_key=True),
    Column('sender_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('recipient_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('amount', Numeric(12, 2), nullable=False, default=0.00),
    Column('timestamp', DateTime, index=True, default=dt.utcnow)
)

currencies = Table(
    'currencies', metadata,
    Column('id', String(3), primary_key=True),
    Column('name', String(150), nullable=False, unique=True),
    Column('rate_rub', Numeric(15, 10), nullable=False),
    Column('multiplier', Numeric(12, 2), nullable=False, default=1)
)


async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = await asyncpgsa.create_pool(dsn=dsn)
    app['db_pool'] = pool
    return pool


def construct_db_url(config):
    DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"
    return DSN.format(
        user=config['DB_USER'],
        password=config['DB_PASS'],
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        port=config['DB_PORT'],
    )


async def get_user_by_id(conn, id):
    result = await conn.fetchrow(
        users
            .select()
            .where(users.c.id == id)
    )
    return result


async def get_user_by_email(conn, email):
    result = await conn.fetchrow(
        users
            .select()
            .where(users.c.email == email)
    )
    return result


async def get_users(conn):
    records = await conn.fetch(
        users.select().order_by(users.c.id)
    )
    return records


async def get_currencies(conn):
    records = await conn.fetch(
        currencies.select().order_by(currencies.c.id)
    )
    return records


async def get_currency_by_id(conn, cur_id):
    result = await conn.fetchrow(
        currencies
            .select()
            .where(currencies.c.id == cur_id)
    )
    return result


async def create_user(conn, email, password, balance, currency):
    stmt = users.insert().values(
        email=email,
        password_hash=generate_password_hash(password),
        balance=balance,
        currency=currency)
    await conn.execute(stmt)
    result = await get_user_by_email(conn, email)
    return result


async def get_transactions(conn):
    records = await conn.fetch(
        transactions.select().order_by(transactions.c.id)
    )
    return records


async def get_user_transactions(conn, user_id):
    sender_email = (select([users.c.email])
                    .where(users.c.id == transactions.c.sender_id)
                    .label("s_email"))
    sender_currency = (select([users.c.currency])
                       .where(users.c.id == transactions.c.sender_id)
                       .label("s_currency"))
    recipient_email = (select([users.c.email])
                       .where(users.c.id == transactions.c.recipient_id)
                       .label("r_email"))
    stmt = (select([transactions, sender_email, sender_currency, recipient_email])
            .where((transactions.c.sender_id == user_id) | (transactions.c.recipient_id == user_id))
            .order_by(transactions.c.timestamp.desc())
            )
    records = await conn.fetch(stmt)
    return records


async def transfer(conn, sender_id, recipient_id, amount):
    stmt = transactions.insert().values(
        sender_id=sender_id, recipient_id=recipient_id, amount=amount)
    await conn.execute(stmt)
    sender = await get_user_by_id(conn, sender_id)
    recipient = await get_user_by_id(conn, recipient_id)
    sender_currency = await get_currency_by_id(conn, sender['currency'])
    recipient_currency = await get_currency_by_id(conn, recipient['currency'])

    new_sender_balance = float(sender['balance']) - amount
    stmt = users.update().where(users.c.id == sender_id).values(balance=new_sender_balance)
    await conn.execute(stmt)

    conversion_amount = await currency_conversion(
        amount,
        *list(map(float, [sender_currency['rate_rub'], sender_currency['multiplier'],
                          recipient_currency['rate_rub'], recipient_currency['multiplier']]))
    )

    new_recipient_balance = float(recipient['balance']) + conversion_amount
    stmt = users.update().where(users.c.id == recipient_id).values(balance=new_recipient_balance)
    await conn.execute(stmt)
