import socket
from core.player import Player
import json
import time
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime
from colorama import Fore, Back, Style
import threading
import inspect
import asyncio
from abc import ABC, abstractmethod

class Bot:
    charLoadComplete= False
    is_joining_map = False
    cmds = []
    index = 0
    monmap = []
    canuseskill = True
    sleep = False
    delayms = 500
    delayuntil = None
    skillNumber = 0
    skillAnim = None
    username = ""
    password = ""
    server = ""
    is_client_connected = False
    serverInfo = None
    client_socket = None
    loaded_quest_ids = []
    registered_auto_quest = []
    items_drop_whitelist = []

    def __init__(
            self, 
            roomNumber: str = None, 
            itemsDropWhiteList = [],
            cmdDelay: int = 500, 
            showLog: bool = True, 
            showDebug: bool = False,
            showChat: bool = True
            ):
        self.roomNumber = roomNumber
        self.showLog = showLog
        self.cmdDelay = cmdDelay
        self.showDebug = showDebug
        self.showChat = showChat
        self.items_drop_whitelist = itemsDropWhiteList
        
    def set_login_info(self, username, password, server):
        self.username = username
        self.password = password
        self.server = server
        
    def start_bot(self):
        self.login(self.username, self.password, self.server)
        asyncio.run(self.connect_client())
        asyncio.run(self.run_commands())
    
    def stop_bot(self):
        self.is_client_connected = False
        if self.client_socket:
            self.client_socket.close()

    def debug(self, *args):
        if not self.showDebug:
            return
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name
        combined_message = ' '.join(map(str, args))
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{caller_name}] {combined_message}")

    def login(self, username, password, server):
        self.player = Player(username, password)
        self.player.getInfo()
        self.serverInfo = self.player.getServerInfo(server)
        
    async def connect_client(self):
        hostname = self.serverInfo[0] 
        port = self.serverInfo[1]
        self.debug(hostname, port)
        host_ip = socket.gethostbyname(hostname)
        self.debug(f'connecting to server {hostname}')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_ip, port))
        self.is_client_connected = True

    async def run_commands(self):    
        if self.is_client_connected:
            # self.print_commands()
            print("Running bot commands...")
        
        while self.is_client_connected:
            messages = self.read_batch(self.client_socket)
            if messages:
                for msg in messages:
                    await self.handle_server_response(msg)
            if self.delayuntil:
                if self.delayuntil > time.time():
                    time.sleep(0.01)
                    continue
                else:
                    self.delayuntil = time.time() + int(self.delayms)/1000
            else:
                self.delayuntil = time.time() + int(self.delayms)/1000
            if self.sleep:
                if self.sleepUntil > time.time():
                    time.sleep(0.01)
                    continue
                else:
                    self.sleep = False
                    if self.player.ISDEAD:
                        self.debug(Fore.MAGENTA + "respawned" + Fore.WHITE)
                        self.write_message(f"%xt%zm%resPlayerTimed%{self.areaId}%{self.user_id}%")
                        self.jump_cell(self.player.CELL, self.player.PAD)
                        self.player.ISDEAD = False
                        self.startAggro()
                        continue
            if self.charLoadComplete:
                if self.is_joining_map:
                    continue
                if self.index >= len(self.cmds):
                    self.index = 0
                cmd = self.cmds[self.index]
                self.handle_command(cmd)           
                self.index += 1
                self.sleepUntil = time.time() + 1
        print('BOT STOPPED\n')
        
    def print_commands(self):
        print("Index\tCommand")
        print("------------------------------")
        for i, cmd in enumerate(self.cmds):
            print(cmd.to_string())
        print("------------------------------")

    def handle_command(self, command):  
        if self.showLog:
            cmd_string = command.to_string()
            if cmd_string:
                cmd_string = cmd_string.split(':')
                if len(cmd_string) > 1:
                    print(Fore.BLUE + f"[{self.index}] {cmd_string[0]}:" + Fore.WHITE + cmd_string[1] + Fore.WHITE)
                else:
                    print(Fore.BLUE + f"[{self.index}] {cmd_string[0]}" + Fore.WHITE)
                
        command.execute(self)
        self.doSleep(self.cmdDelay)
        return

    async def handle_server_response(self, msg):
        if "slow down" in msg:
            self.debug(Fore.RED + msg + Fore.WHITE)
        if "counter" in msg.lower():
            self.debug(Fore.RED + msg + Fore.WHITE)
        if "logout" in msg.lower():
            raise CustomError("LOGOUT")

        if self.is_valid_json(msg):
            data = json.loads(msg)
            try:
                data = data["b"]["o"]
            except:
                return
            cmd = data["cmd"]
            if cmd == "moveToArea":
                self.monmap = data.get("monmap")
                self.mondef = data.get("mondef")
                self.areaName = data["areaName"]
                self.areaId = data["areaId"]
                self.strMapName = data["strMapName"]
                self.monsters = []
                if self.mondef != None and self.monmap != None:
                    for iMonMap in self.monmap:
                        for iMonDef in self.mondef:
                            if iMonMap["MonID"] == iMonDef["MonID"]:
                                mon = iMonMap
                                mon["name"] = iMonDef["strMonName"]
                                self.monsters.append(mon)
            elif cmd == "initUserDatas":
                try:
                    for i in data["a"]:
                        self.player.CHARID = i["data"]["CharID"]
                        self.player.GOLD = int(i["data"]["intGold"])
                    retrieveInventory = f"%xt%zm%retrieveInventory%{self.areaId}%{self.username_id}%"
                    self.player.loadBank()
                    self.write_message(retrieveInventory)
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif cmd == "loadInventoryBig":
                self.charLoadComplete = True
                self.player.INVENTORY = data["items"]
                self.player.FACTIONS = data.get("factions", [])
                for item in self.player.INVENTORY:
                    if item["bEquip"] == 1:
                        if item["sType"] in self.player.listTypeEquip:
                            self.player.EQUIPPED[item["sType"]] = item
                        elif item["sES"] == "Weapon":
                            self.player.EQUIPPED["Weapon"] = item
            elif cmd == "sAct":
                self.player.SKILLS = data["actions"]["active"]
            elif cmd == "stu":
                if data["sta"].get("$tha"):
                    self.player.CDREDUCTION = data["sta"].get("$tha")
            elif cmd == "ct":
                anims = data.get("anims")
                a = data.get("a")
                m = data.get("m")
                p = data.get("p")
                
                if anims:
                    if self.username_id in anims[0]["cInf"]:
                        animsStr = anims[0].get("animStr")
                        if animsStr == self.skillAnim:
                            self.canuseskill = True
                            self.player.updateTime(self.skillNumber)
                    msg = anims[0].get("msg")
                    if msg:
                        pass
                if m:
                    pass
                
            elif cmd == "seia":
                self.player.SKILLS[5]["anim"] = data["o"]["anim"]
                self.player.SKILLS[5]["cd"] = data["o"]["cd"]
                self.player.SKILLS[5]["tgt"] = data["o"]["tgt"]
                print(f"Skills: {self.player.SKILLS}")
            elif cmd == "playerDeath":
                if int(data["userID"]) == self.player.LOGINUSERID:
                    print(Fore.RED + "DEATH" + Fore.WHITE)
                    self.player.ISDEAD = True
                    self.stopAggro()
                    self.doSleep(11000)
            elif cmd == "getQuests":
                pass
            elif cmd == "addGoldExp":
                self.player.GOLD += data["intGold"]
                self.player.GOLDFARMED += data["intGold"]
                gold_added = data["intGold"]
                debug_data_gold = {
                    "gold_added": gold_added,
                    "gold_farmed": self.player.GOLDFARMED,
                    "gold_now": self.player.GOLD
                }
                intExp = data.get("intExp", 0)
                if intExp > 0:
                    self.player.EXPFARMED += intExp
                    debug_data_exp = {
                        "exp_added": intExp,
                        "exp_farmed": self.player.EXPFARMED
                    }
                    self.debug(Fore.BLUE + str(debug_data_exp) + Fore.WHITE)
                self.debug(Fore.YELLOW + str(debug_data_gold) + Fore.WHITE)
            elif cmd == "dropItem":
                dropItems = data.get('items')
                for itemDrop in dropItems.values():
                    if itemDrop["sName"] in self.items_drop_whitelist:
                        self.get_drop(self.user_id, itemDrop["ItemID"])
                        self.player.INVENTORY.append(itemDrop)
                        break
            elif cmd == "addItems":
                dropItems = data.get('items')
                inventItemIds = [str(item["ItemID"]) for item in self.player.INVENTORY]
                tempInventItemIds = [str(item["ItemID"]) for item in self.player.TEMPINVENTORY]
                for itemId, dropItem in dropItems.items():
                    # Item inventory
                    if dropItem.get("CharItemID", None):
                        if itemId in inventItemIds:
                            for playerItem in self.player.INVENTORY:
                                if str(playerItem["ItemID"]) == itemId:
                                    playerItem["iQty"] = dropItem["iQtyNow"]
                                    playerItem["CharItemID"] = dropItem["CharItemID"]
                                    break
                        else:
                            self.player.INVENTORY.append(dropItem)
                    # Item temp inventory
                    else:
                        if itemId in tempInventItemIds:
                            for playerItem in self.player.TEMPINVENTORY:
                                if str(playerItem["ItemID"]) == itemId:
                                    playerItem["iQty"] += dropItem["iQty"]
                                    break
                        else:
                            self.player.TEMPINVENTORY.append(dropItem)
            elif cmd == "turnIn":
                sItems = data.get("sItems").split(':')
                itemId = sItems[0]
                iQty = int(sItems[1])
                for i, temp_item in enumerate(self.player.TEMPINVENTORY):
                    if str(temp_item["ItemID"]) == itemId:
                        if temp_item["iQty"] - iQty == 0:
                            del self.player.TEMPINVENTORY[i]
                        else:
                            temp_item["iQty"] -= iQty
                for i, temp_item in enumerate(self.player.INVENTORY):
                    if str(temp_item["ItemID"]) == itemId:
                        if temp_item["iQty"] - iQty == 0:
                            del self.player.TEMPINVENTORY[i]
                        else:
                            temp_item["iQty"] -= iQty
            elif cmd == "event":
                print(Fore.GREEN + data["args"]["zoneSet"] + Fore.WHITE)
                if data["args"]["zoneSet"]  == "A":
                    if self.strMapName.lower() == "ultraspeaker":
                        self.walk_to(100, 321)
                        time.sleep(0.5)
            elif cmd == "ccqr":
                quest_id = data.get('QuestID', None)
                s_name = data.get('sName', None)
                faction_id = data.get('rewardObj', {}).get('FactionID', None)
                i_rep = data.get('rewardObj', {}).get('iRep', None)
                if int(quest_id) in self.registered_auto_quest:
                    self.accept_quest(quest_id)
                print(Fore.YELLOW + f"ccqr: [{datetime.now().strftime('%H:%M:%S')}] id:{quest_id} name:{s_name} faction:{faction_id}-{i_rep}" + Fore.WHITE)
            elif cmd == "Wheel":
                dropItems = data.get('dropItems')
                dropItemsName = [item["sName"] for item in dropItems.values() if "sName" in item]
                print(Fore.YELLOW + f"Wheel: {dropItemsName}" + Fore.WHITE)
                
        elif self.is_valid_xml(msg):
            if ("<cross-domain-policy><allow-access-from domain='*'" in msg):
                self.write_message(f"<msg t='sys'><body action='login' r='0'><login z='zone_master'><nick><![CDATA[SPIDER#0001~{self.player.USER}~3.0098]]></nick><pword><![CDATA[{self.player.TOKEN}]]></pword></login></body></msg>")
                return
            elif "joinOK" in msg:
                self.extract_user_ids(msg)
                return
            elif "userGone" in msg:
                self.extract_remove_user(msg)
                return
            elif "uER" in msg:
                self.extract_new_user(msg)
                root = ET.fromstring(msg)
                newId = root.find(".//u").get("i")
                msg = f"%xt%zm%retrieveUserData%{self.areaId}%{newId}%"
                self.write_message(msg)
                return
            
        elif msg.startswith("%") and msg.endswith("%"):
            if f"%xt%server%-1%Profanity filter On.%" in msg:
                self.write_message(f"%xt%zm%firstJoin%1%")
                self.write_message(f"%xt%zm%cmd%1%ignoreList%$clearAll%")
            elif "You joined" in msg:
                if msg.split('"')[1].split("-")[0] == "battleon":
                    if self.charLoadComplete is False:
                        msg = f"%xt%zm%retrieveUserDatas%{self.areaId}%{self.username_id}%"
                        self.write_message(msg)
                        self.is_joining_map = False
                else:
                    self.is_joining_map = False
                    self.jump_cell("Enter", "Spawn")
            elif "respawnMon" in msg:
                pass
            elif "chatm" in msg:
                if self.showChat:
                    msg = msg.split('%')
                    text = msg[4].replace("zone~", ": ").replace("guild~", "[GUILD]: ").replace("party~", "[PARTY]: ")
                    sender = msg[5]
                    print(Fore.MAGENTA + f"[{datetime.now().strftime('%H:%M:%S')}] {sender} {text}" + Fore.WHITE)
            elif "whisper" in msg:
                if self.showChat:
                    msg = msg.split('%')
                    text = msg[4]
                    sender = msg[5]
                    print(Fore.MAGENTA + f"[{datetime.now().strftime('%H:%M:%S')}] {sender} [WHISPER] : {text}" + Fore.WHITE)
            elif f"%xt%uotls%-1%{self.player.USER}%afk:true%" in msg:
                pass

    def read_batch(self, conn):
        message_builder = ""
        complete_messages = []
        while True:
            try:
                conn.settimeout(0.5)
                buf = conn.recv(1024) 
                if not buf:
                    print("Connection closed by the server.")
                    self.is_client_connected = False
                    break
                message_builder += buf.decode('utf-8')
                if not message_builder.endswith("\x00"):
                    continue
                messages = message_builder.split("\x00")
                for i, msg in enumerate(messages):
                    msg = msg.strip()
                    if self.is_valid_json(msg):
                        complete_messages.append(msg)
                    elif self.is_valid_xml(msg):
                        complete_messages.append(msg)
                    elif msg.startswith("%") and msg.endswith("%"):
                        complete_messages.append(msg)
                if complete_messages:
                    return complete_messages
            except socket.timeout:
                return
            except Exception as e:
                return f"Error reading data: {e}"
        return complete_messages
    
    def write_message(self, message):
        if self.client_socket is None:
            return "Error: Connection is not established"
        try:
            self.client_socket.sendall((message + "\x00").encode('utf-8'))
        except socket.error as e:
            return f"Error writing to the connection: {e}"
        return None

    def is_valid_json(self, s):
        try:
            json.loads(s)
            return True
        except json.JSONDecodeError:
            return False

    def is_valid_xml(self, s):
        try:
            ElementTree.fromstring(s)
            return True
        except ElementTree.ParseError:
            return False
        
    def get_drop(self, user_id, item_id):
        packet = f"%xt%zm%getDrop%{user_id}%{item_id}%"
        # print(f"getting drop... {item_id}")
        self.write_message(packet)
    
    def accept_quest(self, quest_id: int):
        if not quest_id in self.loaded_quest_ids:
            self.write_message(f"%xt%zm%getQuests%{self.areaId}%{quest_id}%")
            self.loaded_quest_ids.append(quest_id)
            self.doSleep(500)
        self.write_message(f"%xt%zm%acceptQuest%{self.areaId}%{quest_id}%")
        self.doSleep(500)
        
    def turn_in_quest(self, quest_id: int):
        self.write_message(f"%xt%zm%tryQuestComplete%{self.areaId}%{quest_id}%-1%false%1%wvz%")
        self.doSleep(500)

    def use_scroll(self, monsterid, max_target, scroll_id):
        self.target = [f"i1>m:{i}" for i in monsterid][:max_target]
        self.write_message(f"%xt%zm%gar%1%0%{','.join(self.target)}%{scroll_id}%wvz%")
        
    def use_potion(self, potion_id):
        self.target = [f"i1>p:{i}" for i in monsterid][:targetMax]
        self.write_message(f"%xt%zm%gar%1%0%i1>p:{self.user_id}%{potion_id}%wvz%")

    def use_skill_to_monster(self, skill, monsterid, max_target):
        self.target = [f"a{skill}>m:{i}" for i in monsterid][:max_target]
        self.write_message(f"%xt%zm%gar%1%0%{','.join(self.target)}%wvz%")

    def use_skill_to_player(self, skill, max_target):
        target = [f"a{skill}>p:{i}" for i in self.user_ids][:max_target]
        self.write_message(f"%xt%zm%gar%1%0%{','.join(target)}%wvz%")

    def doSleep(self, sleepms):
        self.sleep = True
        self.sleepUntil = time.time() + int(sleepms)/1000.0

    def extract_user_ids(self, xml_message: str):
        root = ET.fromstring(xml_message)
        self.user_ids = []
        self.username_id = None
        for user in root.findall(".//u"):
            self.user_id = user.get("i")  # Get the id
            self.user_ids.append(self.user_id)  # Append to the list
            name = user.find("n").text  # Get the username
            if name == self.player.USER:
                self.username_id = self.user_id  # Store the ID of the target username

    def extract_new_user(self, xml_message: str):
        root = ET.fromstring(xml_message)
        newId = root.find(".//u").get("i")
        self.user_ids.append(newId)
    
    def extract_remove_user(self, xml_message: str):
        root = ET.fromstring(xml_message)
        toRemove = root.find(".//user").get("id")
        for i in self.user_ids:
            if i == toRemove:
                self.user_ids.remove(i)
                break
        
    def jump_cell(self, cell, pad):
        msg = f"%xt%zm%moveToCell%{self.areaId}%{cell}%{pad}%"
        self.player.CELL = cell
        self.player.PAD = pad
        self.write_message(msg)

    def walk_to(self, x, y, speed = 8):
        self.write_message(f"%xt%zm%mv%{self.areaId}%{x}%{y}%{speed}%")

    def reset_cmds(self):
        self.cmds = []
        
    def add_cmd(self, cmd):
        self.cmds.append(cmd)
        
    def add_cmds(self, cmds):
        self.cmds.extend(cmds)

class CustomError(Exception):
    """Exception raised for custom error in the application."""

    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"