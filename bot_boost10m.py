from core.bot import Bot
import commands as cmd
from templates import attack

b = Bot(
    roomNumber=9909,
    itemsDropWhiteList=["GOLD Boost! (10 min)", "CLASS Boost! (10 min)", "REPUTATION Boost! (10 min)", "Moglinberries", "Trollola Nectar", "Nimblestem"],
    cmdDelay=500,
    showLog=True,
    showDebug=False,
    showChat=True
)

b.set_login_info("u", "p", "twilly")

def createCommand(mapName:str, cellpad: list[str], itemName: str, itemQty: int, monsName: str):
    skillCmd = cmd.UseSkillCmd()
    return [
        cmd.JoinMapCmd(mapName, 9909),
        cmd.HuntMonsterCmd(monsName, True),
        cmd.LabelCmd(itemName),
        skillCmd.createSkill(0, monsName),
        skillCmd.createSkill(2),
        skillCmd.createSkill(3),
        skillCmd.createSkill(1),
        skillCmd.createSkill(4),
        cmd.IsNotInInvCmd(itemName, itemQty),
        cmd.ToLabelCmd(itemName),
        cmd.JumpCmd("Enter", "Spawn")
    ]

b.add_cmds([
    cmd.LabelCmd("start"),
    cmd.AcceptQuestCmd(6208)
] + createCommand("nibbleon", ["r10", "Left"], "Moglinberries", 3, "Dark Makai")
  + createCommand("bloodtusk", ["r4", "Center"], "Trollola Nectar", 2, "Trollola Plant")
  + createCommand("cloister", ["r2", "Left"], "Nimblestem", 1, "Acornent")
  + [
      cmd.TurnInQuestCmd(6208),
      cmd.ToLabelCmd("start")
  ]
)


b.start_bot()
