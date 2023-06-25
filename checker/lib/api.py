import json
import requests

from user_agent import generate_user_agent
from urllib.parse import quote

STATUS_UP = 'UP'
STATUS_DOWN = 'DOWN'
STATUS_CORRUPT = 'CORRUPT'
STATUS_MUMBLE = 'MUMBLE'


class ApiException(Exception):
    status: str
    trace: str
    verbose_description: str

    def __init__(self, status, trace, description):
        self.status = status
        self.trace = trace
        self.description = description


def status_check(f):
    def wrapper(session, *args, **kwargs):
        session.headers['User-Agent'] = generate_user_agent()  # random user agent every time
        fname = f.__name__
        try:
            answer = f(session, *args, **kwargs)
            answer.raise_for_status()
        except requests.Timeout as e:
            raise ApiException(STATUS_DOWN, 'Connection timed out', str(e))
        except requests.ConnectionError as e:
            raise ApiException(STATUS_DOWN, 'Connection failed', str(e))
        except requests.HTTPError as e:
            raise ApiException(STATUS_MUMBLE, f'Failed to {fname}: unexpected status code {answer.status_code}', f'{answer.status_code}')
        except Exception as e:
            raise ApiException(STATUS_DOWN, f'Failed to {fname}', str(e))
        return answer

    return wrapper


def index(session: requests.Session, url: str):
    pass


@status_check
def register(session: requests.Session, url: str, username: str, email: str, password1: str, password2: str):
    data = {'username': username, 'password1': password1, 'password2': password2, 'email': email}
    answer = session.post(f'{url}/register', json=data)
    return answer


@status_check
def login(session: requests.Session, url: str, username: str, password: str):
    data = {'username': username, 'password': password}
    answer = session.post(f'{url}/login', json=data)
    return answer


@status_check
def login_without_password(session: requests.Session, url: str, username: str):
    data = {'username': username}
    answer = session.post(f'{url}/login', json=data)
    return answer


@status_check
def get_users(session, url):
    answer = session.get(f'{url}/get_users')
    return answer


@status_check
def get_permissions(session, url, user_id):
    answer = session.get(f'{url}/get_permissions?user_id={user_id}')
    return answer


@status_check
def get_my_permissions(session, url):
    answer = session.get(f'{url}/get_my_permissions')
    return answer


@status_check
def set_permissions(session, url, user_id, permissions):
    answer = session.post(f'{url}/set_permissions', json={'user_id': user_id, 'permissions': permissions})
    return answer


@status_check
def change_password(session, url, user_id, password):
    answer = session.post(f'{url}/change_password', data={'user_id': user_id, 'password': password})
    return answer


@status_check
def change_password_exploit(session, url, user_id1, password1, user_id2, password2):
    answer = session.post(f'{url}/change_password?user_id={user_id2}&password={quote(password2)}',
                          data={'user_id': user_id1, 'password': password1})
    return answer


@status_check
def get_state(session, url):
    answer = session.get(f'{url}/get_state')
    return answer


@status_check
def get_element(session, url, element_path):
    return session.get(f'{url}/elements/{element_path}')


@status_check
def get_elements(session, url):
    return session.get(f'{url}/elements')


@status_check
def execute_element(session, url, element_path, method, args: list):
    return session.post(f'{url}/elements/{element_path}', json={'method': method, 'args': args})


@status_check
def reset_state(session, url):
    return session.post(f'{url}/reset_state')


@status_check
def get_backup(session, url, backup_id):
    return session.get(f'{url}/get_backup', json={'backup_id': backup_id})


@status_check
def admin_get_user(session, url, user_id):
    return session.get(f'{url}/admin/user/{user_id}')


@status_check
def admin_users(session, url):
    return session.get(f'{url}/admin/users')


@status_check
def admin_home(session, url):
    return session.get(f'{url}/admin/home')
