import threading
from datetime import datetime, timedelta, time
import logging

# Dictionary to store target times and timers for each task
tasks = {}
lock = threading.Lock()

DAY_TO_IDX = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

def _to_allowed_weekdays(scheduled_days):
    if not scheduled_days:
        return None
    allowed = {DAY_TO_IDX[d] for d in scheduled_days if d in DAY_TO_IDX}
    return allowed if allowed else None

def _next_target_datetime(now: datetime, hour: int, minute: int, allowed_weekdays: set | None) -> datetime:
    candidate = datetime.combine(now.date(), time(hour=hour, minute=minute))


    if candidate < now:
        candidate += timedelta(days=1)

    if allowed_weekdays is None:
        return candidate

    for _ in range(8):
        if candidate.weekday() in allowed_weekdays:
            return candidate
        candidate += timedelta(days=1)

    # fallback (shouldn't happen)
    return candidate

def schedule_task(task_id, hour, minute, func, scheduled_days=None, *args, **kwargs):
    global tasks
    with lock:
        now = datetime.now()
        allowed_weekdays = _to_allowed_weekdays(scheduled_days)
        target_time = _next_target_datetime(now, hour, minute, allowed_weekdays)
        delay = (target_time - now).total_seconds()

        def task_wrapper():
            if allowed_weekdays is None or target_time.weekday() in allowed_weekdays:
                func(*args, **kwargs)
            # Reschedule the task for the next day (same time)
            schedule_task(task_id, hour, minute, func, scheduled_days, *args, **kwargs)

        # Cancel the previous timer if it exists
        if task_id in tasks:
            tasks[task_id]["timer"].cancel()

        # Schedule the function to be called after the delay
        timer = threading.Timer(max(0, delay), task_wrapper)
        timer.start()

        # Store the new timer, target time, and task details (needed for manual rescheduling)
        tasks[task_id] = {
            "timer": timer,
            "target_time": target_time,
            "hour": hour,
            "minute": minute,
            "scheduled_days": list(scheduled_days) if scheduled_days else None,
            "func": func,
            "args": args,
            "kwargs": kwargs,
        }

def reschedule_task(task_id):
    """
    Manually reschedule an already-scheduled task to the next day at the same time.
    If the task isn't found, raises a KeyError.
    """
    global tasks
    with lock:
        if task_id not in tasks:
            raise KeyError(f"Task '{task_id}' not found")

        info = tasks[task_id]
        info["timer"].cancel()

        now = datetime.now()
        allowed_weekdays = _to_allowed_weekdays(info["scheduled_days"])
        next_target_time = _next_target_datetime(now, info["hour"], info["minute"], allowed_weekdays)
        delay = (next_target_time - now).total_seconds()

        def task_wrapper():
            if allowed_weekdays is None or next_target_time.weekday() in allowed_weekdays:
                info["func"](*info["args"], **info["kwargs"])
            # Reschedule the task for the next day (same time)
            schedule_task(task_id, info["hour"], info["minute"], info["func"], info["scheduled_days"], *info["args"], **info["kwargs"])

        # Arm a new timer
        timer = threading.Timer(max(0, delay), task_wrapper)
        timer.start()

        # Update stored state
        info["timer"] = timer
        info["target_time"] = next_target_time

def cancel_task(task_id):
    global tasks
    with lock:
        if task_id in tasks:
            tasks[task_id]["timer"].cancel()
            del tasks[task_id]

def get_scheduled_tasks():
    global tasks
    with lock:
        return {task_id: task_info["target_time"] for task_id, task_info in tasks.items()}
