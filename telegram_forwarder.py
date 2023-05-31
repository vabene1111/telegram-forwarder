import configparser
import json
import os

from telethon import TelegramClient, events

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_STORAGE_LIMIT = 10000

config = configparser.ConfigParser()
config.read("config.ini")

client = TelegramClient(
    'client',
    config["telegram"]["api_id"],
    config["telegram"]["api_hash"],
    system_version="4.16.30-vxCUSTOM"
)

bot = TelegramClient(
    'bot',
    config["telegram"]["api_id"],
    config["telegram"]["api_hash"],
)

MAIN_GROUP = -952148710


def get_channel_list(data):
    chanel_list = []
    for c in data['channels']:
        chanel_list.append(c['chat_id'])
    return chanel_list


def get_channel_name(data, chat_id):
    for c in data['channels']:
        if c['chat_id'] == chat_id:
            return c['name']
    return "Error"


@client.on(events.NewMessage())
async def tg_incoming_message_handler(event):
    data = load_data()
    if event.message.chat_id == MAIN_GROUP:
        if event.message.text.lower().startswith('/blacklist'):
            word = event.message.text.replace('/blacklist', '').strip().lower()
            data['word_blacklist'].append(word)
            save_data(data)
            await client.send_message(MAIN_GROUP, f'Added {word} to blacklist')
        if event.message.text.startswith('/show'):
            blacklist_string = "**Current Blacklist** \n"
            for w in data['word_blacklist']:
                blacklist_string += f'{w}\n'
            await client.send_message(MAIN_GROUP, blacklist_string)
    else:
        if event.message.chat_id in get_channel_list(data):
            if not is_blacklisted(event.message.text, data) and not is_duplicate(event.message.text, data):
                data['messages'].insert(0, event.message.text)
                data['messages'] = data['messages'][:MESSAGE_STORAGE_LIMIT]
                save_data(data)
                #await bot.send_message(MAIN_GROUP, f'Found in {get_channel_name(data, event.message.chat_id)}')
                await client.forward_messages(MAIN_GROUP, event.message)


def is_blacklisted(message, data):
    for w in data['word_blacklist']:
        if w.lower() in message.lower():
            print(f'found blacklisted word {w.encode("utf-8")} in message {message.encode("utf-8")}')
            return True
    return False


def is_duplicate(message, data):
    for m in data['messages']:
        if m.lower() == message.lower():
            print(f'found duplicate message {message.encode("utf-8")}')
            return True
    return False


def load_data():
    try:
        f = open(os.path.join(BASE_DIR, "data.json"), encoding="UTF-8", )
        data = json.loads(f.read())
        return data
    except FileNotFoundError:
        return {}


def save_data(data):
    f = open(os.path.join(BASE_DIR, "data.json"), "w", encoding="UTF-8", )
    f.write(json.dumps(data))


client.start(config["telegram"]["client_phone"], config["telegram"]["client_pw"])
print('Started client')
bot.start(bot_token=config["telegram"]["bot_token"])


async def main():
    print('Listing Channels you are a member of')
    # async for dialog in client.iter_dialogs():
    #     if dialog.is_channel:
    #         print(f'{dialog.id}, #{dialog.title}')

    print('Listening to incoming messages')
    # data = load_data()
    # channel_string = "- \n".join(get_channel_list(data))
    # blacklist_string = "- \n".join(data["word_blacklist"])
    # await bot.send_message(MAIN_GROUP, f'Bot started listening to channels:\n { channel_string} \n\n Blacklisted words are:\n{ blacklist_string}')
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
