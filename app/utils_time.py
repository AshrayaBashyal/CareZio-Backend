from datetime import datetime, date, time as dt_time
from zoneinfo import ZoneInfo
from typing import Union

NEPAL_TZ = ZoneInfo("Asia/Kathmandu")

def local_time_to_nepal_timeobj(local_time: Union[str, dt_time]) -> dt_time:
    """
    Convert a Nepal local time (string "HH:MM[:SS]" or time object)
    to a Nepal time object.
    """
    if isinstance(local_time, str):
        parts = [int(p) for p in local_time.split(":")]
        h, m = parts[0], parts[1]
        s = parts[2] if len(parts) > 2 else 0
        local_time_obj = dt_time(h, m, s)
    else:
        local_time_obj = local_time

    # ensure tz-aware datetime is in Nepal TZ (if needed)
    local_dt = datetime.combine(date.today(), local_time_obj, tzinfo=NEPAL_TZ)
    return dt_time(local_dt.hour, local_dt.minute, local_dt.second)

def nepal_time_to_str(time_obj: dt_time) -> str:
    """
    Convert a Nepal time object to string "HH:MM:SS".
    """
    return time_obj.isoformat(timespec="seconds")
