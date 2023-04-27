from datetime import datetime, timedelta, date, time, timezone

def turn_datetime_to_longint(dt):
    return int(dt.timestamp()*1000)

def date_return(today, day_offset = 0, duration= 1):
    d = today.date()
    t = time(0,0)
    fromDate = datetime.combine(d, t) + timedelta(days=day_offset)
    toDate = fromDate + timedelta(days = duration)
    return fromDate, toDate

def yesterday_return(today):
    d = today.date()
    t = time(0,0)
    toDate = datetime.combine(d, t)
    fromDate = toDate - timedelta(days=1)
    
    return fromDate, toDate

def today_return(today):
    d = today.date()
    t = time(0,0)
    fromDate = datetime.combine(d, t)
    toDate = fromDate + timedelta(days=1)
    
    return fromDate, toDate