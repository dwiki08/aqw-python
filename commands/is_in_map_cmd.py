from core.bot import Bot
from abstracts.command import Command

class IsInMapCmd(Command):
    
    def __init__(self, mapName: str):
        self.mapName = mapName
    
    def execute(self, bot: Bot):
        if(self.mapName.lower() != bot.strMapName.lower()):
            bot.index += 1
        
    def to_string(self):
        return f"Is in map : {self.mapName}"