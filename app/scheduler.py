import logging
import threading
from datetime import date, datetime, time, timedelta

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

    return candidate


def schedule_task(task_id, hour, minute, func, scheduled_days=None, *args, **kwargs):
    global tasks
    with lock:
        now = datetime.now()
        allowed_weekdays = _to_allowed_weekdays(scheduled_days)
        target_time = _next_target_datetime(now, hour, minute, allowed_weekdays)
        delay = (target_time - now).total_seconds()

        def task_wrapper():
            with lock:
                before_target = tasks.get(task_id, {}).get("target_time")

            try:
                if allowed_weekdays is None or target_time.weekday() in allowed_weekdays:
                    func(*args, **kwargs)
            except Exception:
                logging.exception("Error in scheduled task '%s'", task_id)
            finally:
                with lock:
                    after_target = tasks.get(task_id, {}).get("target_time")

                # Only auto-reschedule if func() didn't already call reschedule_task
                if before_target == after_target:
                    schedule_task(task_id, hour, minute, func, scheduled_days, *args, **kwargs)

        if task_id in tasks:
            tasks[task_id]["timer"].cancel()

        timer = threading.Timer(max(0, delay), task_wrapper)
        timer.start()

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


def reschedule_task(task_id, next_fire_date: date = None):
    """
    Reschedule a task. If next_fire_date is given the task fires on that exact date
    (weekday restrictions are ignored). Otherwise advances to the next natural occurrence.
    """
    global tasks
    with lock:
        if task_id not in tasks:
            raise KeyError(f"Task '{task_id}' not found")

        info = tasks[task_id]
        info["timer"].cancel()

        now = datetime.now()
        allowed_weekdays = _to_allowed_weekdays(info["scheduled_days"])

        if next_fire_date is not None:
            next_target_time = datetime.combine(
                next_fire_date, time(hour=info["hour"], minute=info["minute"])
            )
        else:
            next_target_time = _next_target_datetime(
                now, info["hour"], info["minute"], allowed_weekdays
            )

        delay = (next_target_time - now).total_seconds()

        def task_wrapper():
            with lock:
                before_target = tasks.get(task_id, {}).get("target_time")

            try:
                # Explicit next_fire_date bypasses the weekday check
                if next_fire_date is not None or allowed_weekdays is None or next_target_time.weekday() in allowed_weekdays:
                    info["func"](*info["args"], **info["kwargs"])
            except Exception:
                logging.exception("Error in scheduled task '%s'", task_id)
            finally:
                with lock:
                    after_target = tasks.get(task_id, {}).get("target_time")

                if before_target == after_target:
                    schedule_task(
                        task_id,
                        info["hour"],
                        info["minute"],
                        info["func"],
                        info["scheduled_days"],
                        *info["args"],
                        **info["kwargs"],
                    )

        timer = threading.Timer(max(0, delay), task_wrapper)
        timer.start()

        info["timer"] = timer
        info["target_time"] = next_target_time


def cancel_task(task_id):
    global tasks
    with lock:
        if task_id in tasks:
            tasks[task_id]["timer"].cancel()
            del tasks[task_id]


def schedule_once(task_id: str, target_datetime: datetime, func, *args, **kwargs):
    """Schedule a one-shot task at a specific datetime. Does not auto-reschedule."""
    global tasks
    with lock:
        if task_id in tasks:
            tasks[task_id]["timer"].cancel()

        now = datetime.now()
        delay = (target_datetime - now).total_seconds()

        def task_wrapper():
            try:
                func(*args, **kwargs)
            except Exception:
                logging.exception("Error in scheduled one-shot task '%s'", task_id)
            finally:
                with lock:
                    tasks.pop(task_id, None)

        timer = threading.Timer(max(0, delay), task_wrapper)
        timer.start()

        tasks[task_id] = {
            "timer": timer,
            "target_time": target_datetime,
            "hour": target_datetime.hour,
            "minute": target_datetime.minute,
            "scheduled_days": None,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "once": True,
        }


def get_scheduled_tasks():
    global tasks
    with lock:
        return {task_id: task_info["target_time"] for task_id, task_info in tasks.items()}
