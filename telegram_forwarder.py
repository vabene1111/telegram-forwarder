import configparser
import json
import os
import traceback

from telethon import TelegramClient, events

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGE_STORAGE_LIMIT = 10000
VERSION = '1.0.0'

config = configparser.ConfigParser()
config.read("config.ini")
DEBUG = config.getboolean('telegram', 'DEBUG')

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


def debug(message):
    if DEBUG:
        print(message)


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
            if word != '':
                if word in data['word_blacklist']:
                    data['word_blacklist'].remove(word)
                    save_data(data)
                    await client.send_message(MAIN_GROUP, f'⚫ **Removed** {word} to blacklist')
                else:
                    data['word_blacklist'].append(word)
                    save_data(data)
                    await client.send_message(MAIN_GROUP, f'⚫ Added {word} to blacklist')
            else:
                blacklist_string = "\n".join(data["word_blacklist"])
                await client.send_message(MAIN_GROUP, f'⚫ **Current Blacklist** \n{blacklist_string}')
        if event.message.text.lower().startswith('/whitelist'):
            word = event.message.text.replace('/whitelist', '').strip().lower()
            if word != '':
                if word in data['word_whitelist']:
                    data['word_whitelist'].remove(word)
                    save_data(data)
                    await client.send_message(MAIN_GROUP, f'⚪ **Removed** {word} to whitelist')
                else:
                    data['word_whitelist'].append(word)
                    save_data(data)
                    await client.send_message(MAIN_GROUP, f'⚪ **Added** {word} to whitelist')
            else:
                whitelist_string = "\n".join(data["word_whitelist"])
                await client.send_message(MAIN_GROUP, f'⚪ **Current Whitelist** \n{whitelist_string}')
        if event.message.text.startswith('/help'):
            await client.send_message(MAIN_GROUP, f'**TelegramForwarder Version {VERSION}** \n/help to show this message\n/blacklist to show the blacklist\n/blacklist <word> to add or remove a word from the blacklist\n'
                                      + f'/whitelist to show the whitelist\n /whitelist <word> to add or remove a word from the whitelist'
                                      + '/channel to list channels linked to the bot\n/channel chat_id channel_name')
        if event.message.text.startswith('/channel'):
            word = event.message.text.replace('/channel', '').strip().lower()
            if word != '':
                try:
                    chat_id = word.split(' ')[0]
                    name = ' '.join(word.split(' ')[1:])
                    data['channels'].append({'chat_id': chat_id, 'name': name})
                    save_data(data)
                    await client.send_message(MAIN_GROUP, f'Added channel {name} with chat id {chat_id}')
                except Exception as e:
                    traceback.print_exc()
                    await client.send_message(MAIN_GROUP, f'Failed to add channel with input {event.message.text}')
            else:
                channel_string = ''
                for c in data["channels"]:
                    channel_string += f'**{c["chat_id"]}** - {c["name"]}\n'
                await client.send_message(MAIN_GROUP, f'**Listening to Channels**\n{channel_string}')
    else:
        if event.message.chat_id in get_channel_list(data):
            message_text = event.message.text

            # MAD has random ID's in every post, only take the first part of the post for duplicate/whitelist/blacklist
            try:
                if 'check post authenticity by mad team' in message_text.lower():
                    message_text = message_text.split('\n\n')[0]
            except Exception as e:
                pass

            if is_whitelist(message_text, data) or (not is_blacklisted(message_text, data) and not is_duplicate(message_text, data)):
                data['messages'].insert(0, message_text)
                data['messages'] = data['messages'][:MESSAGE_STORAGE_LIMIT]
                save_data(data)
                # await bot.send_message(MAIN_GROUP, f'Found in {get_channel_name(data, event.message.chat_id)}')
                await client.forward_messages(MAIN_GROUP, event.message)


def is_blacklisted(message, data):
    for w in data['word_blacklist']:
        if w.encode("utf-8").lower() in message.encode("utf-8").lower():
            debug(f'found blacklisted word {w.encode("utf-8")} in message {message.encode("utf-8")}')
            return True
    return False


def is_whitelist(message, data):
    for w in data['word_whitelist']:
        if w.encode("utf-8").lower() in message.encode("utf-8").lower():
            debug(f'found whitelisted word {w.encode("utf-8")} in message {message.encode("utf-8")}')
            return True
    return False


def is_duplicate(message, data):
    for m in data['messages']:
        if m.lower() == message.lower():
            debug(f'found duplicate message {message.encode("utf-8")}')
            return True
    return False


def load_data():
    try:
        f = open(os.path.join(BASE_DIR, "data.json"), encoding="UTF-8", )
        data = json.loads(f.read())
        if 'word_blacklist' not in data:
            data['word_blacklist'] = []
        if 'word_whitelist' not in data:
            data['word_whitelist'] = []
        if 'channels' not in data:
            data['channels'] = []
        if 'messages' not in data:
            data['messages'] = []
        return data
    except FileNotFoundError:
        return {'word_blacklist': [], 'word_whitelist': [], 'channels': [], 'messages': []}


def save_data(data):
    f = open(os.path.join(BASE_DIR, "data.json"), "w+", encoding="UTF-8", )
    f.write(json.dumps(data))


client.start(config["telegram"]["client_phone"], config["telegram"]["client_pw"])
print(f'Started TelegramForwarder client version {VERSION}')
bot.start(bot_token=config["telegram"]["bot_token"])


# TODO all the exception handling / stop detection code does not seem to work
async def main():
    await bot.send_message(MAIN_GROUP, f'🥳 Bot started')

    try:
        await client.run_until_disconnected()
    except Exception:
        await bot.send_message(MAIN_GROUP, f'💥 BOT crashed (1)!')
    await bot.send_message(MAIN_GROUP, f'🛑 BOT stopped!')


try:
    with client:
        client.loop.run_until_complete(main())
except Exception:
    bot.send_message(MAIN_GROUP, f'💥 BOT crashed (2)!')
bot.send_message(MAIN_GROUP, f'🛑 BOT stopped!')
