from telethon import TelegramClient
from telethon.tl.custom.dialog import Dialog
from telethon.tl.custom.message import Message
import asyncio
import os

from libs.models import Config, ApiData

configs: list[Config] = []
for filename in os.listdir("configs"):
    with open(os.path.join("configs", filename), 'r') as file:
        try:
            configs.append(Config.parse_raw(file.read()))
        except Exception as e:
            print("Config error. Details:", e)

config_chats = []
for config in configs:
    config_chats.append(dict([(channel.name, channel_id)
                  for channel_id, channel in enumerate(config.channels)]))

with open("api.json", 'r') as file:
    api = ApiData.parse_raw(file.read())

client = TelegramClient("nicourrrn", api_id=api.id, api_hash=api.hash)



async def main():
    await client.start()

    while True:
        tasks = []
        print("Start again")
        async for dialog in client.iter_dialogs():
            tasks += [start_forwarder(cfg_id, dialog)
                          for cfg_id in range(len(configs))]
        await asyncio.gather(*tasks)
        for config in configs:
            await save_config(config)
        await asyncio.sleep(60)


async def start_forwarder(config_id: int, dialog: Dialog):
    config = configs[config_id]
    chats = config_chats[config_id]
    if dialog.name in chats.keys():
        last_message_id = config.channels[chats[dialog.name]].last_message_id
        messages = await load_messages(dialog, last_message_id, 10)
        if await forward_messages(messages, config.dst_chat.username):
            configs[config_id].channels[chats[dialog.name]].last_message_id = messages[-1].id


async def load_messages(dialog: Dialog, last_message_id: int, limit: int) -> list[Message]:
    messages: list[Message] = await client.get_messages(dialog, limit=limit)
    messages = list(filter(lambda m: m.id > last_message_id, messages))
    return list(reversed(messages))


async def forward_messages(messages: list[Message], dst_username: str) -> bool:
    if len(messages) == 0:
        return False
    for message in messages:
        await message.forward_to(dst_username)
    return True

async def save_config(config: Config):
    with open(os.path.join("configs", f"{config.filename}.json"), 'w') as file:
        file.write(config.json())

if __name__ == '__main__':
    asyncio.run(main())

