from telethon import TelegramClient
import csv
import asyncio

# Load secrets from CSV
with open('data/secrets.csv', mode='r') as file:  # Updated path
    reader = csv.reader(file)
    header = next(reader)
    row = next(reader)

api_id, api_hash, phone_number = row
client = TelegramClient('data/session_name', api_id, api_hash)  # Updated session path

async def get_channel_ids():
    """Retrieve and print the IDs of all chats, including channels and groups."""
    await client.start(phone_number)
    print("Connected! Retrieving chat IDs...")

    async for dialog in client.iter_dialogs():
        chat = dialog.entity
        chat_id = chat.id
        chat_title = chat.title if hasattr(chat, 'title') else "Private Chat"
        chat_username = chat.username if hasattr(chat, 'username') and chat.username else "No Username"

        if hasattr(chat, 'megagroup') and chat.megagroup:
            formatted_id = f"-100{chat_id}"
        elif hasattr(chat, 'broadcast') and chat.broadcast:
            formatted_id = f"-100{chat_id}"
        else:
            formatted_id = str(chat_id)

        print(f"Chat: {chat_title}")
        print(f"Username: @{chat_username}" if chat_username != "No Username" else "Username: None")
        print(f"Chat ID: {formatted_id}")
        print("-" * 50)

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(get_channel_ids())