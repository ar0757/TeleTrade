from telethon import TelegramClient
from telethon import events
import asyncio
import csv
import re
import threading
from trader import execute_trade_with_parameters  # Import the trader function

# Load secrets from CSV
with open('data/secrets.csv', mode='r') as file:
    reader = csv.reader(file)
    header = next(reader)
    row = next(reader)

channel = -1002087162312 # Replace with the telegram channel ID 

api_id, api_hash, phone_number = row
client = TelegramClient('data/session_name', api_id, api_hash)

# Regex patterns to match Telegram messages
pattern_1 = re.compile(
    r"([A-Z]{3}/[A-Z]{3});\s*(\d{2}:\d{2});\s*(PUT|CALL)\s*[🟥🟩]", re.IGNORECASE
)
pattern_2 = re.compile(
    r"([A-Z]{3}\s*/\s*[A-Z]{3})\s*\(OTC\)?-\s*(\d{2}:\d{2})\s*(PUT|CALL)\s*[🔴🟢]", re.IGNORECASE
)

def is_relevant_message(text):
    """Check if the message matches one of the expected formats."""
    return bool(pattern_1.search(text) or pattern_2.search(text))

def extract_info(text):
    """Extract currency pair, time, and direction from the message."""
    match_1 = pattern_1.search(text)
    match_2 = pattern_2.search(text)
    
    if match_1:
        currency_pair, first_time, direction = match_1.groups()
    elif match_2:
        currency_pair, first_time, direction = match_2.groups()
    else:
        return None, None, None
    
    currency1, currency2 = currency_pair.split('/')
    
    return (currency1, currency2), first_time, direction

def run_trader(trading_pair, trade_time, direction):
    """Run the trader function in a separate thread."""
    try:
        # Map Telegram direction (PUT/CALL) to trader direction (sell/buy)
        trader_direction = "sell" if direction.upper() == "PUT" else "buy"
        print(f"Executing trade: Pair={trading_pair}, Time={trade_time}, Direction={trader_direction}")
        
        # Call the trader function
        success = execute_trade_with_parameters(trading_pair, trade_time, trader_direction)
        if success:
            print("Trade execution completed successfully.")
        else:
            print("Trade execution failed.")
    except Exception as e:
        print(f"Error executing trade: {e}")

@client.on(events.NewMessage(chats=channel))
async def handler(event):
    message = event.message
    text = message.text
    
    print(f"New message in channel: {message}")
    print(f"Received Text: {text}")

    if not text or not is_relevant_message(text):
        return
    
    chat = await event.get_chat()
    chat_name = chat.username if hasattr(chat, 'username') and chat.username else chat.id
    
    # Extract the required info
    currencies, first_time, direction = extract_info(text)
    if currencies:
        currency1, currency2 = currencies
        trading_pair = f"{currency1}/{currency2}"
        print(f"New relevant message in {chat_name}:")
        print(f"Currency Pair: {trading_pair}")
        print(f"First Time: {first_time}")
        print(f"Direction: {direction}")
        print("-" * 50)

        # Run the trader in a separate thread to avoid blocking the event loop
        trader_thread = threading.Thread(
            target=run_trader,
            args=(trading_pair, first_time, direction)
        )
        trader_thread.start()

async def main():
    await client.start(phone_number)
    print(f"Connected! Listening for messages in {channel}...")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())