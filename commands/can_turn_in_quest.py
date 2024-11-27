from core.bot import Bot
from abstracts.command import Command

class CanTurnInQuestCmd(Command):
    
    def __init__(self, questId: int):
        self.questId = questId

    def execute(self, bot: Bot):
        if(bot.can_turn_in_quest(self.questId) == False):
            bot.index += 1
        
    def to_string(self):
        return f"Can turn in quest: {self.questId}"