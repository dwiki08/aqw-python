from core.bot import Bot
from templates import attack
from templates.hunt import hunt_item_cmds, hunt_monster_quest_temp_item
import commands as cmd


def makeLabelStoppingQuest(questid):
    return f"STOPPING QUEST {questid}"

item_white_list = [
    "Soldier's Key", # item_white_list[0]
    "Hollowborn Soldier Pinned", # item_white_list[1]
    "Recruit's Brand", # item_white_list[2]
    "Hound's Collar", # item_white_list[3]
    "Hollowborn Collar", # item_white_list[4]
    "Draconian Fang", # item_white_list[5]
    "Glowing Fang", # item_white_list[6]
    "Vindicator Talon", # item_white_list[7]
    "Hollowborn Talon", # item_white_list[8]
    "Grandmaster's Broken Blade", # item_white_list[9]
    "Celestial Gramiel Defeated", # item_white_list[10]
]

b = Bot(
    roomNumber=None, 
    cmdDelay=1000,
    showLog=True, 
    showDebug=False,
    showChat=True)

b.set_login_info("u", "p", "twilly")
private_room_number = 9099
map_name = "dawnsanctum"

UseableMonsters = [
    "Vindicator Soldier", # UseableMonsters[0],
	"Hollowborn Soldier", # UseableMonsters[1],
	"Vindicator Recruit", # UseableMonsters[2],
	"Vindicator Hound", # UseableMonsters[3],
	"Hollowborn Hound", # UseableMonsters[4],
	"Vindicator Draconian", # UseableMonsters[5],
	"Hollowborn Draconian", # UseableMonsters[6],
	"Grandmaster Gramiel", # UseableMonsters[7],
	"Celestial Gramiel", # UseableMonsters[8]
]

b.add_cmds([
    # 9977 | Wunjo, Reversed - Realized
    *hunt_monster_quest_temp_item(
        9977,
        map_name,
        private_room_number,
        UseableMonsters[0]
    ),

    # 9978 | Berkana - Realized
    *hunt_monster_quest_temp_item(
        9978,
        map_name,
        private_room_number,
        UseableMonsters[1]
    ),

    # 9979 | Algiz, Reversed - Realized
    cmd.AcceptQuestCmd(9979),
    cmd.SleepCmd(1000),
    cmd.QuestNotInProgressCmd(9979),
    cmd.ToLabelCmd(makeLabelStoppingQuest(9979)),
    *hunt_item_cmds(
        item_white_list[2],
        5,
        map_name,
        room_number= private_room_number,
        monster_name= UseableMonsters[2],
    ),
    cmd.GetMapItemCmd(13853),
    cmd.SleepCmd(1000),
    cmd.TurnInQuestCmd(9979),
    cmd.LabelCmd(makeLabelStoppingQuest(9979)),


    # 9980 | Gebo - Realized
    *hunt_monster_quest_temp_item(
        9980,
        map_name,
        private_room_number,
        UseableMonsters[3]
    ),

    # 9981 | Eihwaz - Realized
    cmd.AcceptQuestCmd(9981),
    cmd.SleepCmd(1000),
    cmd.QuestNotInProgressCmd(9981),
    cmd.ToLabelCmd(makeLabelStoppingQuest(9981)),
    *hunt_item_cmds(
        item_white_list[4],
        6,
        map_name,
        room_number= private_room_number,
        monster_name= UseableMonsters[4],
    ),
    cmd.GetMapItemCmd(13854),
    cmd.SleepCmd(1000),
    cmd.TurnInQuestCmd(9981),
    cmd.LabelCmd(makeLabelStoppingQuest(9981)),

    # 9982 | Hagalaz - Realized
    *hunt_monster_quest_temp_item(
        9982,
        map_name,
        private_room_number,
        UseableMonsters[5]
    ),

    # 9983 | Mannaz - Realized
    *hunt_monster_quest_temp_item(
        9983,
        map_name,
        private_room_number,
        UseableMonsters[6]
    ),

    # 9984 | Thurisaz - Realized
    cmd.AcceptQuestCmd(9984),
    cmd.SleepCmd(1000),
    cmd.QuestNotInProgressCmd(9984),
    cmd.ToLabelCmd(makeLabelStoppingQuest(9984)),
    *hunt_item_cmds(
        item_white_list[7],
        6,
        map_name,
        room_number= private_room_number,
        monster_name= UseableMonsters[5],
    ),
    *hunt_item_cmds(
        item_white_list[8],
        6,
        map_name,
        room_number= private_room_number,
        monster_name= UseableMonsters[6],
    ),
    cmd.SleepCmd(1000),
    cmd.TurnInQuestCmd(9984),
    cmd.LabelCmd(makeLabelStoppingQuest(9984)),

    # 9985 | Othala - Realized
    *hunt_monster_quest_temp_item(
        9985,
        map_name,
        private_room_number,
        UseableMonsters[7]
    ),

    # 9986 | Isa, Reversed - Realized
    *hunt_monster_quest_temp_item(
        9986,
        map_name,
        private_room_number,
        UseableMonsters[8]
    ),

    cmd.SleepCmd(1000),
    cmd.StopBotCmd("DONE STORY DAWNSANCTUM")
])



b.start_bot()