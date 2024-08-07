from pylitterbot import Account
from datetime import datetime, timedelta
from pydantic import BaseModel
from time import sleep
from os import getenv
from dotenv import load_dotenv
load_dotenv()

LITTERBOT_USERNAME = getenv("LITTERBOT_USERNAME")
LITTERBOT_PASSWORD = getenv("LITTERBOT_PASSWORD")

class LitterReport(BaseModel):
    num_poops: int
    last_poop: str
    is_drawer_full: bool
    drawer_level: int

    def html(self):
        return f"""
        <h4>Litter Robot Report</h4>
        <p>Number of poops: {self.num_poops}</p>
        <p>Last poop: {self.last_poop}</p>
        <p>Is drawer full: {'Yes' if self.is_drawer_full else 'No'}</p>
        <p>Drawer level: {self.drawer_level}%</p>
        <br>
        <p>{'Maybe the litter should go out?' if self.drawer_level > 70 else ':)'}</p>
        """

class LitterBot(object):
    def __init__(self):
        self.username = LITTERBOT_USERNAME
        self.password = LITTERBOT_PASSWORD
        self.robot = None
        self.pets = []
    
    async def get_status_report(self, timezone):
        got_report = False
        num_attempts = 0
        while not got_report:
            try:
                self.account = Account()
                await self.account.connect(username=self.username, 
                                        password=self.password, 
                                        load_robots=True, 
                                        load_pets=True)
                self.pets = self.account.pets
                self.robot = self.account.robots[0]
                activity_history = await self.robot.get_activity_history()
                self.is_drawer_full = self.robot.is_waste_drawer_full
                self.drawer_level = self.robot.waste_drawer_level
                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                poops = [h for h in activity_history if ('name' in dir(h.action) and h.action.name=='CLEAN_CYCLE_COMPLETE' and (datetime.date(h.timestamp)==today or datetime.date(h.timestamp)== yesterday))]
                self.num_poops = len(poops)
                self.last_poop = poops[0].timestamp.astimezone(timezone).strftime('%Y-%m-%d %H:%M:%S')
                got_report = True
            except Exception as e:
                print(f"Error getting litter report. Retrying in 60 seconds. Error: {e}")
                await self.account.disconnect()
                sleep(60)
                num_attempts += 1
                if num_attempts > 15:
                    print("Max attempts reached. Returning default values.")
                    return LitterReport(num_poops=0, last_poop='N/A', is_drawer_full=False, drawer_level=0)
            finally:
                await self.account.disconnect()
        return LitterReport(num_poops=self.num_poops, last_poop=self.last_poop, is_drawer_full=self.is_drawer_full, drawer_level=self.drawer_level)