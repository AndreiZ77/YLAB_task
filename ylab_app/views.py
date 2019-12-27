import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import remember, forget, authorized_userid

from ylab_app import db
from ylab_app.forms import validate_login_form, validate_signup_form, validate_transfer_form


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)


@aiohttp_jinja2.template('index.html')
async def index(request):
    user = await authorized_userid(request)
    if not user:
        raise redirect(request.app.router, 'login')

    async with request.app['db_pool'].acquire() as conn:
        current_user = await db.get_user_by_email(conn, user)
        currency = await db.get_currency_by_id(conn, current_user['currency'])
        transactions = await db.get_user_transactions(conn, current_user['id'])

    return {'user': current_user, 'currency': currency, 'transactions': transactions}


@aiohttp_jinja2.template('login.html')
async def login(request):
    user = await authorized_userid(request)
    if user:
        raise redirect(request.app.router, 'index')

    if request.method == 'POST':
        form = await request.post()

        async with request.app['db_pool'].acquire() as conn:
            error = await validate_login_form(conn, form)
            if error:
                return {'error': error}
            else:
                response = redirect(request.app.router, 'index')
                user = await db.get_user_by_email(conn, form['email'])
                await remember(request, response, user['email'])
                raise response
    return {}


async def logout(request):
    response = redirect(request.app.router, 'login')
    await forget(request, response)
    return response


@aiohttp_jinja2.template('signup.html')
async def signup(request):
    user = await authorized_userid(request)
    if user:
        redirect(request.app.router, 'index')

    async with request.app['db_pool'].acquire() as conn:
        list_currencies = await db.get_currencies(conn)

    if request.method == 'POST':
        form = await request.post()
        async with request.app['db_pool'].acquire() as conn:
            error = await validate_signup_form(conn, form)
            if error:
                return {'list_currencies': list_currencies, 'error': error}
            else:
                response = redirect(request.app.router, 'index')
                user = await db.get_user_by_email(conn, form['email'])
                await remember(request, response, user['email'])
                raise response

    else:
        return {'list_currencies': list_currencies}


@aiohttp_jinja2.template('transfer.html')
async def transfer(request):
    user = await authorized_userid(request)
    if not user:
        raise redirect(request.app.router, 'login')

    async with request.app['db_pool'].acquire() as conn:
        current_user = await db.get_user_by_email(conn, user)
        list_users = await db.get_users(conn)

    if request.method == 'POST':
        form = await request.post()
        async with request.app['db_pool'].acquire() as conn:
            error = await validate_transfer_form(conn, form)
            if error:
                return {'user': current_user, 'list_users': list_users, 'error': error}
            else:
                await db.transfer(conn, current_user['id'], int(form['recipient']), float(form['amount']))
                raise redirect(request.app.router, 'index')
    else:
        return {'user': current_user, 'list_users': list_users}
