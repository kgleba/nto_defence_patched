from access import Permissions
import requests
import time
import json
import re


def wait_for_it(host, port):
    while True:
        try:
            r = requests.get(f'http://{host}:{port}/ping', timeout=2)
            if r.status_code == 200 and r.text == 'pong':
                break
            print(f'Waiting for http://{host}:{port}...', flush=True)
        except Exception as e:
            print(e, flush=True)
        time.sleep(2)


class BadConnection(Exception):
    pass


class ElementDoesntExist(Exception):
    pass


def map_permissions(permissions):
    p = Permissions.NONE
    if permissions & 1:
        p |= Permissions.READ
    if permissions & 2:
        p |= Permissions.WRITE
    return p


class Connector:
    def __init__(self, provider_host, provider_port, database, abi_file):
        wait_for_it(provider_host, provider_port)
        self._url = f'http://{provider_host}:{provider_port}'
        self._session = requests.Session()
        self.import_abi(abi_file)
        self.import_state()
        self._permissions_template = self.generate_permissions_template()
        self.db = database
        self._methods = self.generate_methods()

    def call_external(self):
        pass

    def import_abi(self, abi_file):
        with open(abi_file, 'r') as f:
            abi = json.loads(f.read())
        for k in abi:
            if k == 'inheritance':
                continue
            for f in abi[k]:
                abi[k][f] = map_permissions(abi[k][f])
        self._abi = abi

    def import_state(self):
        r = self._session.get(f'{self._url}/state')
        if r.status_code != 200:
            raise BadConnection
        data = r.json()
        for el in data:
            if el not in self._abi and el not in self._abi['inheritance']:
                raise ElementDoesntExist
        self._state = data

    def execute(self, element_path: str, method: str, args: list[str]):
        if '(' in method:
            method = method[:method.find('(')]
        rdata = {'element': element_path, 'action': method, 'args': args}
        r = self._session.post(f'{self._url}/execute', json=rdata)
        if r.status_code != 200:
            raise BadConnection
        data = r.json()
        result = data['result']
        return result

    def reset_state(self):
        r = self._session.post(f'{self._url}/reset_state')
        if r.status_code != 200:
            raise BadConnection
        return True

    def get_state(self):
        return self._state.copy()

    def get_abi(self):
        return self._abi.copy()

    def get_element_abi(self, element):
        return self._abi[element]

    def get_abi_element_original_name(self, name):
        if name in self._abi:
            return name
        else:
            return self._abi["inheritance"][name]

    def __null_element_permission(self, element):
        tmp = {}
        for k in element:
            if k[0].islower():
                continue
            tmp[k] = self.__null_element_permission(element[k])
        if tmp:
            tmp['self'] = Permissions.NONE
            return tmp
        else:
            return Permissions.NONE

    def generate_permissions_template(self):
        permissions = self.__null_element_permission(self._state.copy())
        return permissions

    def get_permissions_template(self):
        return self._permissions_template.copy()

    def __elements_methods(self, element, name):
        elements = {}
        methods = []
        for m in self._abi[self.get_abi_element_original_name(name)]:
            methods.append(m)
        try:
            methods.remove('get_elements()')
        except:
            pass
        for el in element:
            if el[0].islower():
                continue
            elements[el] = self.__elements_methods(element[el], el)
        return {'elements': elements, 'methods': methods}

    def generate_methods(self):
        methods = {}
        for s in self._state:
            methods[s] = self.__elements_methods(self._state[s], s)
        return {"elements": methods, 'methods': []}

    def get_methods(self):
        return self._methods

    def get_element_methods(self, element_path):
        element_path = element_path.split('.')
        el = self._methods
        for path in element_path:
            el = el['elements'][path]
        return el
