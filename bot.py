from discum.utils.slash import SlashCommander
from discum.utils.button import Buttoner
import discum
import json
import requests
from pymongo import MongoClient

def get_database():
 
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://alan:CVqTP2WEkqnwGmr8@ai-painting.c5uwx70.mongodb.net/test"
    # create the database and collection to start with
    client = MongoClient(CONNECTION_STRING)
    db_client = client['ai_painting']
    db_job = db_client['job']
    # db_job.create_index("prompt")

    return db_job

db_job = get_database()

# To obtain your token, https://discordpy-self.readthedocs.io/en/latest/token.html
TOKEN= 'NTUyNzI2NTQ2ODIyMDcwMjgy.YdPFng.uUxKSWpVFtSdVfVM-cUkgnogxCk'

bot = discum.Client(token=TOKEN,log=False)

WEBHOOK_BOT_ID = "1099816041737101462"
MIDJOURNEY_BOT_ID = "936929561302675456"

current_job = {}

def endpoints(resp):
  if resp.event.message or resp.event.message_updated:
    msg = resp.parsed.auto()
    # Listening to owner sent message
    if msg['author']['id'] == WEBHOOK_BOT_ID:
        content_string = msg['content']
        try:
            content_json = json.loads(content_string)
            cmd = content_json["cmd"]
        except:
            # Not able to parse request body
            return

        if cmd == "imagine":
            try:
                prompt = content_json["msg"]
                user_id = content_json["user_id"]
            except:
                # Not able to parse request body
                return
            try:
                channelID = msg['channel_id']
                guildID = msg['guild_id']
                slashCmds = bot.getSlashCommands(MIDJOURNEY_BOT_ID).json()
                slashCmd = SlashCommander(slashCmds)
                metadata = slashCmd.get(['imagine'])
            except:
                # Not able to fetch neccessary info to send the slash command
                return

            current_job[prompt] = user_id
            print(current_job)
            # Modify slash command metadata 
            metadata['options'] = [{
                "type": 3,
                "name": "prompt",
                "value": prompt
            }]

            bot.triggerSlashCommand(MIDJOURNEY_BOT_ID, channelID,guildID=guildID, data=metadata)

        elif cmd == "button":
            try:
                metadata = content_json['metadata']
                button_name = content_json['button_name']
                user_id = content_json["user_id"]
                prompt: content_json['prompt']

            except:
                # Not able to parse request body
                return
            buts = Buttoner(metadata["components"])
            bot.click(
                MIDJOURNEY_BOT_ID,
                channelID=metadata["channel_id"],
                guildID=metadata["guild_id"],
                messageID=metadata["id"],
                messageFlags=metadata["flags"],
                data=buts.getButton(button_name),
            )
            
    # Listening to midjourney bot sent message
    elif msg['author']['id'] == MIDJOURNEY_BOT_ID:
        prompt_identifier = "**"
        content = msg['content']

        prompt = content[content.find(prompt_identifier)+len(prompt_identifier):content.rfind(prompt_identifier)]
        
        # job wait to start
        if len(msg['attachments']) == 0:
            result_metadata = {
                "prompt": prompt,
                "status": "waiting to start",
                "msg": msg["content"],
                "user_id": current_job[prompt],
                "timestamp": msg['timestamp']
            }
            db_job.insert_one(result_metadata)

        # job started or finished
        elif len(msg['attachments']) == 1:
            
            #job in progress
            if len(msg['components']) == 0:
                result_metadata = {
                    "prompt": prompt,
                    "status": "in progress",
                    "msg": msg["content"],
                    "user_id": current_job[prompt],
                    "timestamp": msg['timestamp']
                }
                db_job.insert_one(result_metadata)

            #job finished
            else:
                try:
                    result_metadata = {
                        'channel_id':msg["channel_id"],
                        'guild_id':msg["guild_id"],
                        'id':msg["id"],
                        'flags':msg["flags"],
                        'components':msg['components'],
                        'attachments':msg['attachments'],
                        'prompt': prompt,
                        "status": "job finished",
                        "user_id": current_job[prompt],
                        "timestamp": msg['timestamp']
                    }
                except:
                    # Not able to parse request body
                    return
                db_job.insert_one(result_metadata)

bot.gateway.command({"function": endpoints})
bot.gateway.run(auto_reconnect=True)
