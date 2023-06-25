import requests
import random
import os

from user_agent import generate_user_agent
from lib.utils import *

MIN_INT = -65535
MAX_INT = 65535
MAX_LIST_N = 4


class Fuzzer:
    def __init__(self, session, url, endpoints, wordlists_dir):
        self.endpoints = endpoints
        self.__load_wordlists(wordlists_dir)
        self.session = session
        self.url = url

        with open('lib/params.txt') as f:
            self.params = f.readlines()

    def __load_wordlists(self, wordlists_dir):
        files = []
        for f in os.listdir(wordlists_dir):
            if f.endswith('.txt'):
                files.append(f)

        self.wordlists = {}
        for f in files:
            with open(f'{wordlists_dir}/{f}', 'r', encoding='utf8') as fr:
                self.wordlists[f] = fr.readlines()

    def generate_param_value(self, type_, payloads=True):
        if type_ == int:
            return random.randint(MIN_INT, MAX_INT)
        elif type_ == str:
            if payloads:
                return self.random_payload()
            return generate_extended_str()
        elif type(type_) == list:
            return [self.generate_param_value(type_[0], payloads=payloads) for _ in range(MAX_LIST_N)]
        elif type(type_) == dict:
            ndict = {}
            for t in type_:
                ndict[t] = self.generate_param_value(type_[t], payloads=payloads)
            return ndict

    def random_payload(self):
        w = random.choice(list(self.wordlists))
        return random.choice(self.wordlists[w])

    def fuzz(self, endpoint, config, any_method=False, any_params=False, params_limit=0):
        if any_method:
            methods = ['GET', 'POST']
        else:
            methods = config['methods']

        method = random.choice(list(methods))
        try:
            params = {}
            for p in config['methods'][method]:
                params[p] = self.generate_param_value(config['methods'][method][p])
        except KeyError:
            params = {}
        if any_params:
            params_limit = random.randint(0, params_limit)
            while params_limit - len(params) > 0:
                ptype = random.choice([int, str])
                pname = random.choice(
                    [generate_str(), random.randint(MIN_INT, MAX_INT), random.choice(self.params), random.choice(self.params),
                     random.choice(self.params)])
                if ptype == str:
                    params[pname] = self.random_payload()
                    continue
                params[pname] = self.generate_param_value(ptype)
        if method == 'GET':
            params_ = '?'
            for p in params:
                params_ += str(p)
                params_ += '='
                params_ += str(params[p])

            return self.session.get(f'{self.url}{endpoint}{params_}')
        else:
            if 'form' in config:
                return self.session.post(f'{self.url}{endpoint}', data=params)
            else:
                return self.session.post(f'{self.url}{endpoint}', json=params)

    def fuzz_random(self, any_method=False, any_params=False, params_limit=0, blacklist=[]):
        endpoint = random.choice(list(self.endpoints))
        while endpoint in blacklist:
            endpoint = random.choice(list(self.endpoints))
        return self.fuzz(endpoint, self.endpoints[endpoint], any_method=any_method, any_params=any_params, params_limit=params_limit)
