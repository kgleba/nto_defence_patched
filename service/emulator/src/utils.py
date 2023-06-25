def map_action(cl, action):
    for act in action.split('.'):
        cl = getattr(cl, act)
    return cl
