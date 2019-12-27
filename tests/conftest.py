import pytest

from db_init import (
    setup_db, teardown_db,
    create_tables, create_sample_data, drop_tables
)
from ylab_app.main import init_app
from ylab_app.settings import load_config, BASE_DIR


@pytest.fixture
async def client(aiohttp_client):
    config = load_config(BASE_DIR / 'config' / 'test_config.toml')
    app = await init_app(config)
    return await aiohttp_client(app)


@pytest.fixture(scope='session')
def database():
    admin_db_config = load_config(
        BASE_DIR / 'config' / 'admin_config.toml')['database']
    test_db_config = load_config(
        BASE_DIR / 'config' / 'test_config.toml')['database']

    setup_db(executor_config=admin_db_config, target_config=test_db_config)
    yield
    teardown_db(executor_config=admin_db_config, target_config=test_db_config)


@pytest.fixture
def tables_and_data(database):
    test_db_config = load_config(
        BASE_DIR / 'config' / 'test_config.toml')['database']

    create_tables(target_config=test_db_config)
    create_sample_data(target_config=test_db_config)

    yield

    drop_tables(target_config=test_db_config)
