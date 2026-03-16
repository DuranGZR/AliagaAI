"""Test scheduler"""
from app.scheduler import init_scheduler, get_scheduled_jobs, shutdown_scheduler

init_scheduler()
jobs = get_scheduled_jobs()

print("SCHEDULER OK")
print(f"Aktif gorevler: {len(jobs)}")
for j in jobs:
    print(f"  - {j['name']}: {j['next_run']}")

shutdown_scheduler()
