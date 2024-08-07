import os
import pickle
import asyncio
from datetime import datetime, timedelta
import pytz

class AsyncTaskRunner:
    def __init__(self, task_time, timezone):
        self.task_time = task_time
        self.timezone = timezone
        self.state_file = "modules/task_state.pkl"
        self.state = {"last_done": None}
    
    async def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "rb") as file:
                self.state = pickle.load(file)
    
    async def save_state(self):
        with open(self.state_file, "wb") as file:
            pickle.dump(self.state, file)
        
    def should_run_task(self):
        now = datetime.now(self.timezone)
        last_done = self.state["last_done"]

        if last_done is None:
            task_time_today = now.replace(hour=self.task_time[0], minute=self.task_time[1], second=self.task_time[2], microsecond=0)
            return now >= task_time_today
        
        if last_done.tzinfo is None:
            last_done = self.timezone.localize(last_done)
        next_run_time = last_done.replace(hour=self.task_time[0], minute=self.task_time[1], second=self.task_time[2], microsecond=0)
        if next_run_time <= last_done:
            next_run_time += timedelta(days=1)
        return now >= next_run_time
    
    async def run_task(self, task):
        await task()
        self.state["last_done"] = datetime.now(self.timezone)
        await self.save_state()
    
    async def run_loop(self, task):
        await self.load_state()
        while True:
            if self.should_run_task():
                await self.run_task(task)
            else:
                next_run = self.get_next_run_time()
                sleep_duration = (next_run - datetime.now(self.timezone)).total_seconds()
                print(f"Task already done today. Next run at {next_run}. Sleeping for {sleep_duration:.2f} seconds.")
                await asyncio.sleep(sleep_duration)
    
    def get_next_run_time(self):
        now = datetime.now(self.timezone)
        next_run = now.replace(hour=self.task_time[0], minute=self.task_time[1], second=self.task_time[2], microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        return next_run