from core.bot import Bot
from templates import afk, attack
import commands as cmd

b = Bot(roomNumber="9099", itemsDropWhiteList=[
  "Rime Token"
  ],showLog=True, showDebug=False, cmdDelay=500)
b.set_login_info("u", "p", "alteon")
atk = attack.generalAttack
b.add_cmds([
  cmd.JoinMapCmd("battlegrounde"),
  cmd.JumpCmd("r2", "Center"),
  cmd.RegisterQuestCmd(3991),
  cmd.RegisterQuestCmd(3992),
  cmd.MessageCmd("Farming..."),
  cmd.LabelCmd("atk"),
] + atk + [
    cmd.ToLabelCmd("atk")
])
b.start_bot()