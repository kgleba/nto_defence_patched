import random
import string
from enum import Flag, auto
from flatten_dict import flatten
from flatten_dict import unflatten


def generate_str(length=None):
    """Generate a random string of fixed length."""
    if not length:
        length = random.randint(10, 20)
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def generate_extended_str(length=None):
    """Generate a random string of fixed length."""
    if not length:
        length = random.randint(10, 20)
    letters = string.ascii_letters + string.digits + r'!#$%&()*+,-./:;<=>?@[]^_`{|}~'
    return ''.join(random.choice(letters) for _ in range(length))


def generate_email(length1=None, length2=None):
    if not length1:
        length1 = random.randint(7, 15)
    if not length2:
        length2 = random.randint(5, 15)
    a = generate_str(length=length1)
    c = random.choice(['ru', 'com', 'net', 'org'])
    b = generate_str(length=length2)
    return f'{a}@{b}.{c}'


class Permissions(Flag):
    NONE = auto()
    READ = auto()
    WRITE = auto()


permissions_template = {"Developers": {"Alarm": 1, "Cameras": 1, "self": 1}, "Elevator": 1,
                        "Head office": {"Alarm": 1, "Cameras": 2, "Elevator": 1, "self": 1},
                        "Security department": {"Alarm": 1, "Cameras": 1, "self": 1},
                        "ServerRoom": {"Alarm": 1, "Cameras": 1, "Elevator": 1, "self": 1}, "self": 1}

full_abi = {"elements": {'Developers': {'elements': {'Alarm': {'elements': {},
                                                               'methods': ['set_sensitivity(sensitivity)', 'get_sensitivity()', 'enable()',
                                                                           'disable()', 'get_enabled()', 'get_type()',
                                                                           'add_element(type,element)']}, 'Cameras': {'elements': {},
                                                                                                                      'methods': [
                                                                                                                          'get_image()',
                                                                                                                          'enable()',
                                                                                                                          'disable()',
                                                                                                                          'get_enabled()',
                                                                                                                          'get_type()',
                                                                                                                          'add_element(type,element)']}},
                                        'methods': ['get_type()', 'add_element(type,element)']}, 'Elevator': {'elements': {}, 'methods': [
    'set_floor(floor)', 'get_floor()', 'enable()', 'disable()', 'get_enabled()', 'get_type()', 'add_element(type,element)']},
                         'Head office': {'elements': {'Alarm': {'elements': {},
                                                                'methods': ['set_sensitivity(sensitivity)', 'get_sensitivity()', 'enable()',
                                                                            'disable()', 'get_enabled()', 'get_type()',
                                                                            'add_element(type,element)']}, 'Cameras': {'elements': {},
                                                                                                                       'methods': [
                                                                                                                           'get_image()',
                                                                                                                           'enable()',
                                                                                                                           'disable()',
                                                                                                                           'get_enabled()',
                                                                                                                           'get_type()',
                                                                                                                           'add_element(type,element)']},
                                                      'Elevator': {'elements': {},
                                                                   'methods': ['set_floor(floor)', 'get_floor()', 'enable()', 'disable()',
                                                                               'get_enabled()', 'get_type()',
                                                                               'add_element(type,element)']}},
                                         'methods': ['get_type()', 'add_element(type,element)']}, 'Security department': {'elements': {
        'Alarm': {'elements': {},
                  'methods': ['set_sensitivity(sensitivity)', 'get_sensitivity()', 'enable()', 'disable()', 'get_enabled()', 'get_type()',
                              'add_element(type,element)']}, 'Cameras': {'elements': {}, 'methods': ['get_image()', 'enable()', 'disable()',
                                                                                                     'get_enabled()', 'get_type()',
                                                                                                     'add_element(type,element)']}},
        'methods': [
            'get_type()',
            'add_element(type,element)']},
                         'ServerRoom': {'elements': {'Alarm': {'elements': {},
                                                               'methods': ['set_sensitivity(sensitivity)', 'get_sensitivity()', 'enable()',
                                                                           'disable()', 'get_enabled()', 'get_type()',
                                                                           'add_element(type,element)']}, 'Cameras': {'elements': {},
                                                                                                                      'methods': [
                                                                                                                          'get_image()',
                                                                                                                          'enable()',
                                                                                                                          'disable()',
                                                                                                                          'get_enabled()',
                                                                                                                          'get_type()',
                                                                                                                          'add_element(type,element)']},
                                                     'Elevator': {'elements': {},
                                                                  'methods': ['set_floor(floor)', 'get_floor()', 'enable()', 'disable()',
                                                                              'get_enabled()', 'get_type()', 'add_element(type,element)']}},
                                        'methods': ['set_backup_url(url)', 'get_backup_url()', 'backup()', 'get_backup_date()',
                                                    'update_data(data)', 'send_backup()', 'full_clean()', 'get_type()',
                                                    'add_element(type,element)']}}, "methods": []}


def get_random_path(abi):
    if abi['elements'] == {}:
        return ''
    branch = random.choice(list(abi['elements']))
    child = get_random_path(abi['elements'][branch])
    if child:
        return branch + '.' + child
    return branch


def apply_permission(permissions, path, p):
    path_ = tuple(path.split('.'))
    flatten_ = flatten(permissions)
    flatten_[path_] = p
    try:
        return unflatten(flatten_)
    except ValueError:
        path_ = tuple((path + '.self').split('.'))
        flatten_ = flatten(permissions)
        flatten_[path_] = p
        return unflatten(flatten_)


def none_permissions(permissions):
    if type(permissions) == int:
        return Permissions.NONE
    tmp = {}
    for p in permissions:
        tmp[p] = none_permissions(permissions[p])
    return tmp


def random_permissions(permissions):
    if type(permissions) == int:
        r = random.choice(list(Permissions))
        return r
    tmp = {}
    for p in permissions:
        tmp[p] = random_permissions(permissions[p])
    return tmp


def import_permissions(permissions):
    if type(permissions) == int:
        return Permissions(permissions)
    tmp = {}
    for p in permissions:
        tmp[p] = import_permissions(permissions[p])
    return tmp


def export_permissions(permissions):
    if type(permissions) == Permissions:
        return permissions.value
    tmp = {}
    for p in permissions:
        tmp[p] = export_permissions(permissions[p])
    return tmp
