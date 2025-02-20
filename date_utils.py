import datetime

days_of_week = [
    ("mon", "monday"), ("tue", "tuesday"), ("wed", "wednesday"), ("thu", "thursday"),
    ("fri", "friday"), ("sat", "saturday"), ("sun", "sunday")
]

def _get_week_index(day):
    return next((i for i, (first, second) in enumerate(days_of_week) if first == day or second == day), -1)

def is_day_between(target_day, start_day, end_day):
    return target_day >= start_day and target_day <= end_day

def extract_date(date_str):
    """expected date_str: "2/20/2025", "2025/02/05", "wed", "wednesday"\n
    returns date object
    """
    _date = None
    try:
        _date = datetime.date.fromisoformat(date_str.replace('/', '-'))
    except ValueError:
        # try day of week name
        if any(date_str in (first, second) for first, second in days_of_week):
            today = datetime.date.today()
            index = _get_week_index(date_str)
            # Calculate days until next Wednesday (weekday=2, where Monday=0, Sunday=6)
            days_until = (index - today.weekday() + 7) % 7 or 7
            _date = today + datetime.timedelta(days=days_until)
    return _date

def extract_time(time_str):
    """expected time_str: "18:45" (24 hr clock)\n
    returns time object
    """
    t = time_str.split(':')
    try:
        hour = int(t[0])
        min = int(t[1]) if len(t) > 1 else 0
        return datetime.time(hour, min)
    except ValueError:
        return None