from .fastapi import app
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, FileResponse
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from datetime import date
from fastapi_scheduler import SchedulerAdmin
from .solar import mine_switcher, last_switch_result
from .solar import last_switch_result
from dotenv import load_dotenv
import os
import secrets
from .settings_ep import get_settings

env = os.getenv('ENV', 'test').lower()  # Default to 'test' if ENV is not set
if env == 'prod':
    dotenv_path = '.env.prod'
elif env == 'test':
    dotenv_path = '.env.test'



security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
def spa(username: str = Depends(get_current_username)):
    # Serve the HTML SPA
    return FileResponse('templates/index.html')

@app.get("/status")
def get_status():
    # Return the miner status as JSON
    miner_status = "on" if last_switch_result else "off"
    return {"status": miner_status}

@app.get("/", response_class=HTMLResponse)
def root():

    # Decide the status of the miner based on the last_switch_result
    miner_status = "an" if last_switch_result else "aus"
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Miner Status</title>
</head>
<body>
    <h1>Miner ist {miner_status}</h1>
</body>
</html>
"""


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