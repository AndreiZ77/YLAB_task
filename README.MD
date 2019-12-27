Task for the company Y_LAB
==========================
Designed using Pithon 3.7 + AIOHTTP (12/2019)


Setup
=====


Clone the repository, create virtualenv if necessary.

Install the packages necessary for work = [
    'aiohttp',
    'aiohttp-jinja2',
    'bcrypt',
    'pytoml',
    'aiohttp_security[session]',
    'aioredis',
    'sqlalchemy',
    'asyncpg',
    'asyncpgsa',
    'psycopg2-binary'
]

To start the application you need running Postgres & Redis servers.

Create db with tables and sample data::

    $ python db_init.py -a

Check db for created data::

    $ psql -h localhost -p $DB_PORT -U postgres -d ylab_task -c "select * from users"

Run server::

    $ python ylab_app/main.py -c config/user_config.toml


(example user/password: ivan@one.com/ivan)

