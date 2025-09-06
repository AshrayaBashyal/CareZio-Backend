from datetime import datetime, date, time as dt_time
from zoneinfo import ZoneInfo
from typing import Union

def local_time_to_utc_timeobj(local_time: Union[str, dt_time], tz_str: str = "Asia/Kathmandu") -> dt_time:
    """
    Convert a local time (string "HH:MM[:SS]" or time object) in timezone tz_str
    to a UTC time object (time in UTC, no date).
    """
    if isinstance(local_time, str):
        parts = [int(p) for p in local_time.split(":")]
        h, m = parts[0], parts[1]
        s = parts[2] if len(parts) > 2 else 0
        local_time_obj = dt_time(h, m, s)
    else:
        local_time_obj = local_time

    local_dt = datetime.combine(date.today(), local_time_obj, tzinfo=ZoneInfo(tz_str))
    utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
    # normalize seconds and microseconds to 0 for scheduler matching
    return dt_time(utc_dt.hour, utc_dt.minute, utc_dt.second)

def utc_time_to_local_str(utc_time_obj: dt_time, tz_str: str = "Asia/Kathmandu") -> str:
    """
    Convert a UTC time object to a local time string ("HH:MM:SS") in given timezone.
    """
    utc_dt = datetime.combine(date.today(), utc_time_obj, tzinfo=ZoneInfo("UTC"))
    local_dt = utc_dt.astimezone(ZoneInfo(tz_str))
    return local_dt.time().isoformat(timespec="seconds")
