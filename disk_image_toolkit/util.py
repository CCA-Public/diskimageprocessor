from datetime import datetime, timezone
import math


def time_to_int(str_time):
    """Convert datetime to unix integer since epoch."""
    try:
        datetime_obj = datetime.strptime(str_time, "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        return int(datetime.timestamp(datetime_obj))
    except ValueError:
        logger.warning(
            f"Date string {str_time} in unexpected format (expected: YYYY-MM-DDTHH-MM-SS). Unable to convert to Unix timestamp."
        )


def human_readable_size(size):
    """Convert size in bytes to human-readable form."""
    if size == 0:
        return "0 bytes"
    size_name = ("bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p)
    s = str(s)
    s = s.replace(".0", "")
    return "{} {}".format(s, size_name[i])
