APPNAME = 'DoelenCalendar'
VERSION = (0, 0, 1, 'alpha', 0)

def get_version(*args, **kwargs):
    from dedoelen.utils.version import get_version
    return get_version(*args, **kwargs)
