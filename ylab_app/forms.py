import re

from ylab_app import db
from ylab_app.security import check_password_hash


async def validate_login_form(conn, form):
    email = form['email']
    password = form['password']

    if not email:
        return 'email is required'
    if not password:
        return 'password is required'

    user = await db.get_user_by_email(conn, email)

    if not user:
        return 'Invalid username'
    if not check_password_hash(password, user['password_hash']):
        return 'Invalid password'
    else:
        return None

    return 'error'


async def validate_signup_form(conn, form):
    email = form['email']
    password = form['password']
    balance = form['balance']
    currency = form['currency']

    if not email:
        return 'email is required'
    if not password:
        return 'password is required'
    if not balance:
        return 'balance is required'
    if not currency:
        return 'currency is required'
    if await db.get_user_by_email(conn, email):
        return 'email has already been registered'
    if not re.fullmatch(r'[-+]?\d{,12}\.?\d{,2}', str(balance)):
        return 'balance is not valid'

    user = await db.create_user(conn, email, password, float(balance), currency)

    if not user:
        return 'Invalid username'
    if not check_password_hash(password, user['password_hash']):
        return 'Invalid password'
    else:
        return None

    return 'error'


async def validate_transfer_form(conn, form):
    recipient = form['recipient']
    amount = form['amount']

    if not recipient:
        return 'recipient is required'
    if not amount:
        return 'amount is required'
    if not re.fullmatch(r'[-+]?\d{,10}\.?\d{,2}', str(amount)):
        return 'amount is not valid'
