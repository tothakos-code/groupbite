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
            # Reschedule the task for the next day
            schedule_task(task_id, hour, minute, func, *args, **kwargs)

        # Cancel the previous timer if it exists
        if task_id in tasks:
            tasks[task_id]["timer"].cancel()

        # Schedule the function to be called after the delay
        timer = threading.Timer(delay, task_wrapper)
        timer.start()

        # Store the new timer and target time
        tasks[task_id] = {
            "timer": timer,
            "target_time": target_time
        }

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
