from datetime import datetime

def is_service_active(service_id, date_str, calendar, calendar_dates):
    date_int = int(date_str)
    
    for ex in calendar_dates:
        if ex['service_id'] == service_id and int(ex['date']) == date_int:
            if ex['exception_type'] == '2': 
                return False
            elif ex['exception_type'] == '1':  
                return True

    if service_id in calendar:
        s = calendar[service_id]
        day_name = datetime.strptime(date_str, "%Y%m%d").strftime('%A').lower()
        if s[day_name] == '1' and int(s['start_date']) <= date_int <= int(s['end_date']):
            return True

    return False



def time_to_seconds(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s