from datetime import datetime, timedelta
from core.config import settings

def align_time_to_interval(now: datetime, interval: int = None) -> datetime:
    """
    Align the given time to the nearest interval.

    Args:
        now (datetime): The current datetime.
        interval (int): The alignment interval in minutes. Defaults to settings.alignment_interval.

    Returns:
        datetime: The aligned datetime, subtracting the interval.
    """
    if interval is None:  # Use settings if no interval is provided
        interval = settings.alignment_interval

    aligned_minutes = (now.minute // interval) * interval
    aligned_time = now.replace(minute=aligned_minutes, second=0, microsecond=0)
    return aligned_time - timedelta(minutes=interval)
