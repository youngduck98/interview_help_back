from datetime import datetime, timedelta, date, time, timezone
import pytz

def turn_datetime_to_longint(dt):
    return int(dt.timestamp()*1000 - 32400000)

def today_return():
    return int(datetime.now(pytz.timezone('Asia/Seoul')).timestamp()*1000 - 32400000)

def date_return(today, day_offset = 0, duration= 1):
    d = today.date()
    t = time(0,0)
    fromDate = datetime.combine(d, t) + timedelta(days=day_offset)
    toDate = fromDate + timedelta(days = duration)
    print("date_return")
    print(fromDate, toDate)
    return fromDate, toDate