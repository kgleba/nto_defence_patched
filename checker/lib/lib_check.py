import random
import string
import base64
import json
import time

from requests.adapters import HTTPAdapter, Response
from user_agent import generate_user_agent
from enum import Flag, auto
from dotenv import dotenv_values

from lib.api import *
from lib.utils import *

config = dotenv_values('env')

timeout = 3
PORT = int(config.get('XSS_PORT', 8080))
ADMIN_LOGIN = config.get('XSS_ADMIN_LOGIN')
ADMIN_PASS = config.get('XSS_ADMIN_PASS')
BASIC_LOGIN = config.get('XSS_BASIC_LOGIN')
BASIC_PASS = config.get('XSS_BASIC_PASS')

backup_url = 'http://control:8080/put_backup_here'


class TimeoutHTTPAdapter(HTTPAdapter):
    def send(self, *args, **kwargs) -> Response:
        kwargs['timeout'] = timeout
        return super().send(*args, **kwargs)


def check(ip):
    url = f'http://{ip}:{PORT}'
    try:
        session = requests.Session()
        session.mount('https://', TimeoutHTTPAdapter(max_retries=2))
        session.mount('http://', TimeoutHTTPAdapter(max_retries=2))
        session.verify = False

        session_admin = requests.Session()
        session_admin.mount('https://', TimeoutHTTPAdapter(max_retries=2))
        session_admin.mount('http://', TimeoutHTTPAdapter(max_retries=2))
        session_admin.verify = False

        session.auth = (BASIC_LOGIN, BASIC_PASS)
        session_admin.auth = (BASIC_LOGIN, BASIC_PASS)

        username = generate_str()
        password = generate_extended_str()
        email = generate_email()

        index(session, url)

        login(session_admin, url, ADMIN_LOGIN, ADMIN_PASS)

        result = reset_state(session_admin, url)

        register(session, url, username, email, password, password)
        user_id = login(session, url, username, password).json()['user_id']

        result = admin_get_user(session_admin, url, user_id)

        password_new = generate_extended_str()
        change_password(session, url, user_id, password_new)

        try:
            login(session, url, username, password_new)
        except ApiException as e:
            if e.status == STATUS_MUMBLE and e.description in ['404', '403']:
                return STATUS_CORRUPT, 'Failed to change password', ''

        user_permissions = get_my_permissions(session, url).json()['permissions']
        if import_permissions(user_permissions) != none_permissions(permissions_template.copy()):
            return STATUS_CORRUPT, 'Wrong initial permissions', ''

        # admin
        permissions = random_permissions(permissions_template.copy())
        users = get_users(session_admin, url).json()['users']

        found = False
        for u in users:
            if u['username'] == username and u['uid'] == user_id:
                found = True

        if not found:
            return STATUS_CORRUPT, 'Created user is not in users list or user id is wrong', ''

        permissions_ = get_permissions(session_admin, url, user_id).json()['permissions']
        if import_permissions(permissions_) != none_permissions(permissions_template.copy()):
            return STATUS_CORRUPT, 'Wrong initial permissions', ''

        set_permissions(session_admin, url, user_id, export_permissions(permissions))

        permissions_ = get_permissions(session_admin, url, user_id).json()['permissions']
        if import_permissions(permissions_) != permissions:
            return STATUS_CORRUPT, 'Permissions were not set', ''

        # elements

        elements = get_elements(session_admin, url).json()
        if elements != full_abi:
            return STATUS_CORRUPT, 'Wrong elements data received', ''

        random_element = random.choice(list(full_abi['elements']))
        element = get_element(session_admin, url, random_element).json()
        if element != full_abi['elements'][random_element]:
            return STATUS_CORRUPT, 'Wrong element data returned', ''

        for _ in range(2):
            random_path = get_random_path(full_abi)
            result = execute_element(session_admin, url, random_path, 'get_type()', []).json()['result']
            if result != random_path.split('.')[-1]:
                return STATUS_CORRUPT, 'Cannot get type of an element', ''

        for _ in range(2):
            random_path = get_random_path(full_abi)
            permissions = none_permissions(permissions_template.copy())
            permissions = apply_permission(permissions, random_path, Permissions.READ | Permissions.NONE)
            set_permissions(session_admin, url, user_id, export_permissions(permissions))
            result = execute_element(session, url, random_path, 'get_type()', []).json()['result']
            if result != random_path.split('.')[-1]:
                return STATUS_CORRUPT, 'Cannot get type of an element', ''

        path = 'ServerRoom.Alarm'
        method = 'enable()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']

        path = 'Developers.Cameras'
        method = 'get_image()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']

        result = reset_state(session_admin, url)

        path = 'Elevator'
        method = 'disable()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']

        result = admin_users(session_admin, url)

        path = 'Elevator'
        method = 'get_enabled()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']
        if result != False:
            return STATUS_CORRUPT, 'Elevator wasn\'t disabled', ''

        path = 'Elevator'
        method = 'enable()'
        args = []
        permissions = none_permissions(permissions_template.copy())
        permissions = apply_permission(permissions, path, Permissions.WRITE | Permissions.READ | Permissions.NONE)
        set_permissions(session_admin, url, user_id, export_permissions(permissions))
        result = execute_element(session, url, path, method, args).json()['result']

        path = 'ServerRoom'
        method = 'set_backup_url()'
        args = [backup_url]
        result = execute_element(session_admin, url, path, method, args).json()['result']

        path = 'ServerRoom'
        method = 'get_backup_url()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']
        if result != backup_url:
            return STATUS_CORRUPT, 'Backup url wasn\'t set', ''

        path = 'ServerRoom'
        method = 'update_data()'
        backup = {generate_str(): generate_extended_str()}
        args = [base64.b64encode(json.dumps(backup).encode()).decode()]
        result = execute_element(session_admin, url, path, method, args).json()['result']

        path = 'ServerRoom'
        method = 'backup()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']

        path = 'ServerRoom'
        method = 'send_backup()'
        args = []
        result = execute_element(session_admin, url, path, method, args).json()['result']

        backup_id = result['backup_id']
        result = get_backup(session_admin, url, backup_id).json()['backup']

        backup_ = json.loads(base64.b64decode(result['backup']).decode())

        if backup_ != backup:
            return STATUS_CORRUPT, 'Backup was modified', ''

        result = admin_home(session_admin, url)

        result = reset_state(session_admin, url)


    except ApiException as e:
        return e.status, e.trace, e.description
    except KeyError as e:
        return STATUS_CORRUPT, 'Key wasn\'t found in a response', ''
    except Exception as e:
        return STATUS_DOWN, 'Something went wrong', str(e)
    return STATUS_UP, 'All functionality checks passed', ''
