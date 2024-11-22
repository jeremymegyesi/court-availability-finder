from datetime import time

def is_day_between(target_day, start_day, end_day):
    # Map days of the week to their ordinal values
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    target = days.index(target_day)
    start = days.index(start_day)
    end = days.index(end_day)
    
    # Check if the target day is within the range
    if start <= end:
        return start <= target <= end
    else:
        # Wrap around the week
        return target >= start or target <= end
    
def extract_time(time_str):
    t = time_str.split(':')
    hour = int(t[0])
    min = int(t[1]) if len(t) > 1 else 0
    return time(hour, min)