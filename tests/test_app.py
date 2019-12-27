from ylab_app.forms import validate_login_form, validate_signup_form, validate_transfer_form
from ylab_app.security import (
    generate_password_hash,
    check_password_hash
)


def test_security():
    user_password = 'pass'
    hashed = generate_password_hash(user_password)
    assert check_password_hash(user_password, hashed)


async def test_index_view(tables_and_data, client):
    resp = await client.get('/')
    assert resp.status == 200


async def test_login_form(tables_and_data, client):
    invalid_form = {
        'email': 'joe@test.com',
        'password': '123'
    }
    valid_form = {
        'email': 'ivan@one.com',
        'password': 'ivan'
    }
    async with client.server.app['db_pool'].acquire() as conn:
        error = await validate_login_form(conn, invalid_form)
        assert error
        no_error = await validate_login_form(conn, valid_form)
        assert not no_error


async def test_login_view(tables_and_data, client):
    invalid_form = {
        'email': 'joe@test.com',
        'password': '123'
    }
    valid_form = {
        'email': 'ivan@one.com',
        'password': 'ivan'
    }
    resp = await client.post('/login', data=invalid_form)
    assert resp.status == 200
    assert 'Invalid username' in await resp.text()

    resp = await client.post('/login', data=valid_form)
    assert resp.status == 200
    assert 'client: ivan@one.com' in await resp.text()


async def test_signup_form(tables_and_data, client):
    invalid_balance = {
        'email': 'test@test.com',
        'password': 'test',
        'balance': 'x099z.777',
        'currency': 'USD'
    }
    duplicate_email = {
        'email': 'ivan@one.com',
        'password': 'ivan',
        'balance': '10000',
        'currency': 'RUB'
    }
    valid_form = {
        'email': 'test@test.com',
        'password': 'test',
        'balance': '3000.50',
        'currency': 'USD'
    }
    async with client.server.app['db_pool'].acquire() as conn:
        error = await validate_signup_form(conn, invalid_balance)
        assert error
        error = await validate_signup_form(conn, duplicate_email)
        assert error
        no_error = await validate_signup_form(conn, valid_form)
        assert not no_error


async def test_signup_view(tables_and_data, client):
    invalid_balance = {
        'email': 'test@test.com',
        'password': 'test',
        'balance': 'x099z.777',
        'currency': 'USD'
    }
    duplicate_email = {
        'email': 'ivan@one.com',
        'password': 'ivan',
        'balance': '10000',
        'currency': 'RUB'
    }
    valid_form = {
        'email': 'test@test.com',
        'password': 'test',
        'balance': '3000.50',
        'currency': 'USD'
    }
    resp = await client.post('/signup', data=invalid_balance)
    assert resp.status == 200
    assert 'balance is not valid' in await resp.text()

    resp = await client.post('/signup', data=duplicate_email)
    assert resp.status == 200
    assert 'email has already been registered' in await resp.text()

    resp = await client.post('/signup', data=valid_form)
    assert resp.status == 200
    assert 'client: test@test.com' in await resp.text()


async def test_transfer_form(tables_and_data, client):
    invalid_amount = {
        'recipient': 2,
        'amount': '1@00.5S',
    }
    valid_amount = {
        'recipient': 2,
        'amount': '1000.55',
    }
    async with client.server.app['db_pool'].acquire() as conn:
        error = await validate_transfer_form(conn, invalid_amount)
        assert error
        no_error = await validate_transfer_form(conn, valid_amount)
        assert not no_error


async def test_transfer_view(tables_and_data, client):
    valid_login = {
        'email': 'ivan@one.com',
        'password': 'ivan'
    }
    await client.post('/login', data=valid_login)

    invalid_amount = {
        'recipient': 2,
        'amount': '1@00.5S',
    }
    valid_amount = {
        'recipient': 2,
        'amount': '1000.55',
    }
    resp = await client.post('/transfer', data=invalid_amount)
    assert resp.status == 200
    assert 'amount is not valid' in await resp.text()

    resp = await client.post('/transfer', data=valid_amount)
    assert resp.status == 200
    assert 'client: ivan@one.com' in await resp.text()

