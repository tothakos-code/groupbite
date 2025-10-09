import threading
from datetime import datetime, timedelta
import logging

# Dictionary to store target times and timers for each task
tasks = {}
lock = threading.Lock()

def schedule_task(task_id, hour, minute, func, *args, **kwargs):
    global tasks
    with lock:
        now = datetime.now()
        target_time = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=hour, minutes=minute)

        # If the target time is earlier than the current time, schedule for the next day
        if target_time < now:
            target_time += timedelta(days=1)

        delay = (target_time - now).total_seconds()

        def task_wrapper():
            func(*args, **kwargs)
            # Reschedule the task for the next day (same time)
            schedule_task(task_id, hour, minute, func, *args, **kwargs)

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

        # Cancel the currently scheduled timer
        info["timer"].cancel()

        # Compute next day's target at the same scheduled time
        next_target_time = info["target_time"] + timedelta(days=1)
        now = datetime.now()
        delay = (next_target_time - now).total_seconds()

        def task_wrapper():
            info["func"](*info["args"], **info["kwargs"])
            # Continue the usual daily reschedule
            schedule_task(task_id, info["hour"], info["minute"], info["func"], *info["args"], **info["kwargs"])

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
