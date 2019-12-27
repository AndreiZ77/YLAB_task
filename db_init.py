from sqlalchemy import create_engine, MetaData

from ylab_app.db import construct_db_url
from ylab_app.db import users, transactions, currencies
from ylab_app.security import generate_password_hash
from ylab_app.settings import load_config


def setup_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']
    db_pass = target_config['DB_PASS']

    with engine.connect() as conn:
        teardown_db(executor_config=executor_config,
                    target_config=target_config)

        conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                     (db_name, db_user))


def teardown_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']

    with engine.connect() as conn:
        # terminate all connections to be able to drop database
        conn.execute("""
          SELECT pg_terminate_backend(pg_stat_activity.pid)
          FROM pg_stat_activity
          WHERE pg_stat_activity.datname = '%s'
            AND pid <> pg_backend_pid();""" % db_name)
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP ROLE IF EXISTS %s" % db_user)


def get_engine(db_config):
    db_url = construct_db_url(db_config)
    engine = create_engine(db_url, isolation_level='AUTOCOMMIT')
    return engine


def create_tables(target_config=None):
    engine = get_engine(target_config)

    meta = MetaData()
    meta.create_all(bind=engine, tables=[users, transactions, currencies])


def drop_tables(target_config=None):
    engine = get_engine(target_config)

    meta = MetaData()
    meta.drop_all(bind=engine, tables=[users, transactions, currencies])


def create_sample_data(target_config=None):
    engine = get_engine(target_config)
    #EUR, USD, GPB, RUB, BTC
    with engine.connect() as conn:
        conn.execute(currencies.insert(), [
            {'id': 'RUB',
             'name': 'Russian Ruble',
             'rate_rub': 1,
             'multiplier': 1},
            {'id': 'USD',
             'name': 'American dollar',
             'rate_rub': 1/61.72,
             'multiplier': 1},
            {'id': 'EUR',
             'name': 'Euro',
             'rate_rub': 1/68.41,
             'multiplier': 1},
            {'id': 'GPB',
             'name': 'Great Britain Pound',
             'rate_rub': 1/80.11,
             'multiplier': 1},
            {'id': 'BTC',
             'name': 'Bitcoin',
             'rate_rub': 1/445.72,
             'multiplier': 1}
        ])
        conn.execute(users.insert(), [
            {'email': 'ivan@one.com',
             'password_hash': generate_password_hash('ivan'),
             'balance': 10000.00,
             'currency': 'RUB'},
            {'email': 'bob@two.com',
             'password_hash': generate_password_hash('bob'),
             'balance': 3000.00,
             'currency': 'USD'},
            {'email': 'adam@three.com',
             'password_hash': generate_password_hash('adam'),
             'balance': 5000.00,
             'currency': 'EUR'},
        ])
        conn.execute(transactions.insert(), [
            {'sender_id': 1, 'recipient_id': 2, 'amount': 150.20},
            {'sender_id': 1, 'recipient_id': 3, 'amount': 80.50},
            {'sender_id': 3, 'recipient_id': 2, 'amount': 700},
        ])





if __name__ == '__main__':
    user_db_config = load_config('config/user_config.toml')['database']
    admin_db_config = load_config('config/admin_config.toml')['database']

    import argparse
    parser = argparse.ArgumentParser(description='DB related shortcuts')
    parser.add_argument("-c", "--create",
                        help="Create empty database and user with permissions",
                        action='store_true')
    parser.add_argument("-d", "--drop",
                        help="Drop database and user role",
                        action='store_true')
    parser.add_argument("-r", "--recreate",
                        help="Drop and recreate database and user",
                        action='store_true')
    parser.add_argument("-a", "--all",
                        help="Create sample data",
                        action='store_true')
    args = parser.parse_args()

    if args.create:
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
    elif args.drop:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
    elif args.recreate:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
    elif args.all:
        teardown_db(executor_config=admin_db_config,
                    target_config=user_db_config)
        setup_db(executor_config=admin_db_config,
                 target_config=user_db_config)
        create_tables(target_config=user_db_config)
        create_sample_data(target_config=user_db_config)
    else:
        parser.print_help()
