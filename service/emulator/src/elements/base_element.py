import json
from exceptions import InvalidElement


class BaseElement:
    def __init__(self, type_: str):
        self._elements = {}
        self._type = type_

    def add_element(self, type_, element):
        if not isinstance(element, BaseElement) and not type(element) == str:
            raise InvalidElement
        self._elements[type_] = element

    def _public_attrs(self):
        return [attr for attr in self.__dict__ if not attr.startswith('_')]

    def __iter__(self):
        for attr in self._public_attrs():
            yield attr, self.__getattribute__(attr)
        for el in self._elements:
            yield el, dict(self._elements[el])
        return
        yield

    def get_type(self):
        return self._type

    def get_elements_json(self):
        elements = {}
        for el in self._elements:
            elements[el] = dict(self._elements[el])
        return elements

    def get_elements(self):
        return self._elements
