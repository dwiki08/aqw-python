from core.bot import Bot
from abstracts.command import Command

class IsNotInMapCmd(Command):
    
    def __init__(self, mapName: str):
        self.mapName = mapName
    
    def execute(self, bot: Bot):
        if(self.mapName.lower() == bot.strMapName.lower()):
            bot.index += 1
        
    def to_string(self):
        return f"Is not in map : {self.mapName}"