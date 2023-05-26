import configparser
import json
import os

from telethon import TelegramClient, events

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_STORAGE_LIMIT = 5000

config = configparser.ConfigParser()
config.read("config.ini")

client = TelegramClient(
    'client',
    config["telegram"]["api_id"],
    config["telegram"]["api_hash"],
    system_version="4.16.30-vxCUSTOM"
)

MAIN_GROUP = -952148710


def get_channel_list(data):
    chanel_list = []
    for c in data['channels']:
        chanel_list.append(c['chat_id'])


@client.on(events.NewMessage())
async def tg_incoming_message_handler(event):
    print('{}'.format(event))

    data = load_data()
    if event.message.chat_id == MAIN_GROUP:
        if event.message.text.startswith('/blacklist'):
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
                await client.forward_messages(MAIN_GROUP, event.message)


def is_blacklisted(message, data):
    for w in data['word_blacklist']:
        if w.lower() in message.lower():
            print(f'found blacklisted word {w} in message {message}')
            return True
    return False


def is_duplicate(message, data):
    for m in data['messages']:
        if m.lower() in message.lower():
            print(f'found duplicate message {message}')
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


async def main():
    print('Listing Channels you are a member of')
    # async for dialog in client.iter_dialogs():
    #     if dialog.is_channel:
    #         print(f'{dialog.id}, #{dialog.title}')

    print('Listening to incoming messages')
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())
