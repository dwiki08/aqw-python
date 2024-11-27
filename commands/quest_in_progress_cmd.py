from core.bot import Bot
from abstracts.command import Command

class QuestInProgressCmd(Command):
    
    def __init__(self, questId: int):
        self.questId = questId

    def execute(self, bot: Bot):
        loaded_quest_ids = [loaded_quest["QuestID"] for loaded_quest in bot.loaded_quest_datas]
        if not str(self.questId) in str(loaded_quest_ids):
            bot.index += 1
        
    def to_string(self):
        return f"Can turn in quest: {self.questId}"