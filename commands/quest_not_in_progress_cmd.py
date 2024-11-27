from core.bot import Bot
from abstracts.command import Command

class QuestNotInProgressCmd(Command):
    
    def __init__(self, questId: int):
        self.questId = questId

    def execute(self, bot: Bot):
        loaded_quest_ids = [loaded_quest["QuestID"] for loaded_quest in bot.loaded_quest_datas]
        if str(self.questId) in str(loaded_quest_ids):
            bot.index += 1
        
    def to_string(self):
        return f"Quest not in progress: {self.questId}"