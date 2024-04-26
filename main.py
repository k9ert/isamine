from fastapi import FastAPI
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from datetime import date
from fastapi_scheduler import SchedulerAdmin
from solar import mine_switcher

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


# Create `AdminSite` instance
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))

# Create an instance of the scheduled task scheduler `SchedulerAdmin`
scheduler = SchedulerAdmin.bind(site)

# Add scheduled tasks, refer to the official documentation: https://apscheduler.readthedocs.io/en/master/
# use when you want to run the job at fixed intervals of time
@scheduler.scheduled_job('interval', seconds=6)
def interval_task_test():
    mine_switcher()

@app.on_event("startup")
async def startup():
    # Mount the background management system
    #site.mount_app(app)
    # Start the scheduled task scheduler
    scheduler.start()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True)