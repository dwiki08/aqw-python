from core.bot import Bot
from abstracts.command import Command

class GetMapItemCmd(Command):
    
    def __init__(self, map_item_id: int):
        self.map_item_id = map_item_id

    def execute(self, bot: Bot):
        bot.write_message(f"%xt%zm%getMapItem%{bot.areaId}%{self.map_item_id}%")
        
    def to_string(self):
        return f"Get map item: {self.map_item_id}"