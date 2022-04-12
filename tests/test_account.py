import os
import sys
import random
import logging
import time
import decimal
from pathlib import Path
from functools import partial
import requests
import multiprocessing
from multiprocessing.pool import Pool as ProcessPool
from multiprocessing.pool import ThreadPool

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ['SETTINGS_CONFIGURATION'] = 'test'


from app import create_app
from utils.test import get_test_session, create_test_db
from apps.account.models import Account
from settings.test import TestConfig
import pytest

API_URL = f'http://{TestConfig.HOST}:{TestConfig.PORT}/api/account'

def _start_test_serv():
    import logging
    app = create_app()
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run(threaded=True, host=TestConfig.HOST, port=TestConfig.PORT)


def _req_to_api(n, session, uuid, method, *args, **kwargs):
    amount = round(decimal.Decimal(random.choice(range(10, 10000)) / 100), 2)

    if method == 'tg':
        method = random.choice(['deposit', 'withdraw'])

    data = {'account_uuid': str(uuid), "amount": str(amount)}
    res = requests.post(f'{API_URL}/{method}/', json=data)

    if res.status_code == 400 and res.json().get('code') == 'locked':
        return _req_to_api(n, session, uuid, method)

    if res.status_code == 400 and res.json().get('code') == 'lack_of':
        return None, method

    return (-amount if method == 'withdraw' else amount), method


def _make_request(n):

    print(f'Start worker {n}')

    with get_test_session() as session:
        acc = Account()
        session.add(acc)
        session.commit()

        threads_count = random.choice(range(80, 100))
        print(f'Threads {threads_count}')
        with ThreadPool() as pool:

            # deposit
            fnc = partial(_req_to_api, uuid=acc.uuid, session=session, method='deposit')
            res = pool.map(fnc, range(threads_count))
            result_balance = sum(amount for amount, method in res if amount is not None)
            session.refresh(acc)
            current_balance = acc.balance
            print(result_balance, current_balance, 'DEPOSIT', f'Worker {n}')
            assert current_balance == result_balance, 'Deposit API'

            # withdraw
            fnc = partial(_req_to_api, uuid=acc.uuid, session=session, method='withdraw')
            res = pool.map(fnc, range(threads_count+20))
            withdrawn = abs(sum(amount for amount, method in res if amount is not None))

            assert result_balance >= withdrawn, 'Negative balance'
            result_balance = current_balance - withdrawn
            session.refresh(acc)
            current_balance = acc.balance
            print(result_balance, current_balance, 'WITHDRAW', f'Worker {n}')
            assert current_balance == result_balance, 'WithDraw API'

            # together

            acc.balance = 0
            session.commit()

            fnc = partial(_req_to_api, uuid=acc.uuid, session=session, method='tg')
            res = pool.map(fnc, range(threads_count))

            result_balance = sum(amount for amount, method in res if amount is not None)
            session.refresh(acc)

            current_balance = acc.balance
            print(result_balance, current_balance, 'TOGETHER', f'Worker {n}')
            assert current_balance == result_balance, 'Together API'


def _test_concurrency():
    accounts_count = 5

    with ProcessPool() as pool:
        # sub process per account
        pool.map(_make_request, range(accounts_count))


def _test_api():

    res = requests.post(f'{API_URL}/_make_user/')
    res.raise_for_status()

    account_uuid = res.json()['account_uuid']

    deposit = round(decimal.Decimal(random.choice(range(1000, 10000)) / 100), 2)
    res = requests.post(f'{API_URL}/deposit/', json={'account_uuid': account_uuid, "amount": str(deposit)})
    res.raise_for_status()

    withdraw = round(decimal.Decimal(random.choice(range(100, 1000)) / 100), 2)
    res = requests.post(f'{API_URL}/withdraw/', json={'account_uuid': account_uuid, "amount": str(withdraw)})
    res.raise_for_status()

    res = requests.get(f'{API_URL}/balance/{account_uuid}/')
    res.raise_for_status()

    cur_balance = decimal.Decimal(res.json()['balance'])
    assert cur_balance == deposit - withdraw, 'Test API'

    withdraw = cur_balance + 1
    res = requests.post(f'{API_URL}/withdraw/', json={'account_uuid': account_uuid, "amount": str(withdraw)})

    assert res.status_code == 400 and res.json()['code'] == 'lack_of', 'Negative balance'

    res = requests.get(f'{API_URL}/balance/{account_uuid}/')

    assert cur_balance == decimal.Decimal(res.json()['balance'])


def test_account():
    with create_test_db():
        server_proc = multiprocessing.Process(target=_start_test_serv)
        server_proc.start()
        time.sleep(2)

        _test_concurrency()
        _test_api()

        server_proc.terminate()
        server_proc.join()


if __name__ == '__main__':
    test_account()