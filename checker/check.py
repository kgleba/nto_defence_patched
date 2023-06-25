from lib.lib_check import check


def run(ip):
    status, trace, description = check(ip)
    result = {'status': status, 'trace': trace, 'description': description}
    return result
