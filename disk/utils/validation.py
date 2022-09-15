from datetime import datetime


def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return False
    return True
