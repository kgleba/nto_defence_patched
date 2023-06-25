import json
from collections import Counter

base_office = {'Cameras': {'enabled': True}, 'Alarm': {'enabled': True, 'sensitivity': 3}}

server_room = {'Cameras': {'enabled': True}, 'Alarm': {'enabled': True, 'sensitivity': 5}, 'Elevator': {'enabled': True, 'floor': 1},
               'backup_url': '', 'backup_date': '', 'data': ''}

sections = {'Elevator': {'enabled': True, 'floor': 1}, 'Head office': base_office | {'Elevator': {'enabled': True}},
            'Developers': base_office, 'Security department': base_office, 'ServerRoom': server_room}

data = json.dumps(sections)
with open('dump.json', 'w') as f:
    f.write(data)

# abi

base_element_m = {"get_type()": 1, "get_elements()": 1, "add_element(type,element)": 3}

section_m = base_element_m

server_room_m = {"set_backup_url(url)": 3, "get_backup_url()": 1, "backup()": 3, "get_backup_date()": 1, "update_data(data)": 3,
                 "send_backup()": 1, "full_clean()": 3} | section_m

controller_m = {"enable()": 3, "disable()": 3, "get_enabled()": 1} | base_element_m

alarm_m = {"set_sensitivity(sensitivity)": 3, "get_sensitivity()": 1} | controller_m

cameras_m = {"get_image()": 1} | controller_m

elevator_m = {"set_floor(floor)": 3, "get_floor()": 1} | controller_m

abi = {"Section": section_m, "Controller": controller_m, "ServerRoom": server_room_m, "Alarm": alarm_m, "Cameras": cameras_m,
       "Elevator": elevator_m, 'inheritance': {'Head office': 'Section', 'Developers': 'Section', 'Security department': 'Section'}}

with open('abi.json', 'w') as f:
    f.write(json.dumps(abi))

with open('../../control/data/abi.json', 'w') as f:
    f.write(json.dumps(abi))
