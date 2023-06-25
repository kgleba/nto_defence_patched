import json
from elements import Alarm, Cameras, Controller, Elevator, Section, ServerRoom

str_to_class = {'Alarm': Alarm, 'Cameras': Cameras, 'Controller': Controller, 'Elevator': Elevator, 'ServerRoom': ServerRoom}


class State:
    def __init__(self, state_file):
        self.import_(state_file)

    def __import_section(self, type_, section):
        if type_ in str_to_class:
            element = str_to_class[type_]()
        else:
            element = Section(type_)
        for el in section:
            if el in str_to_class:
                e = str_to_class[el]()
                for attr in section[el]:
                    setattr(e, attr, section[el][attr])
                element.add_element(el, e)
            elif el[0].istitle():
                element.add_element(el, self.__import_section(el, section[el]))
            else:
                setattr(element, el, section[el])
        return element

    def import_(self, state_file):
        with open(state_file, 'r') as f:
            file_data = f.read()
        data = json.loads(file_data)
        self._elements = {}
        for k in data:
            v = data[k]
            self._elements[k] = self.__import_section(k, v)

    def export_(self):
        exported = {}
        for el in self._elements:
            exported[el] = dict(self._elements[el])
        return exported

    def get_elements(self):
        return self._elements
