from dotenv import load_dotenv
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import sqlite3
import datetime

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# Create the client and connect
client = TelegramClient('AIAST', api_id, api_hash)

async def ensure_client_connected():
    print('Start checking connection...')
    if not await client.connect():
        print('Not connected. Connecting...')
        await client.connect()
        print('Connected successfully.')
    if not await client.is_user_authorized():
        print('User not authorized. Sending code request...')
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))
    print('Client is connected and authorized.')

# Function to convert datetime to string
def adapt_datetime(ts):
    return ts.strftime('%Y-%m-%d %H:%M:%S')

# Function to convert string to datetime
def convert_datetime(ts):
    return datetime.datetime.strptime(ts.decode('utf-8'), '%Y-%m-%d %H:%M:%S')

# Register the adapter and converter
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('timestamp', convert_datetime)

async def fetch_messages(chat_id, limit=100):
    history = await client(GetHistoryRequest(
        peer=PeerChannel(chat_id),
        offset_id=0,
        offset_date=None,
        add_offset=0,
        limit=limit,
        max_id=0,
        min_id=0,
        hash=0
    ))

    messages = history.messages
    for message in messages:
        # print(message.text)
        print(message.message)
        store_message(chat_id, message.sender_id, message.message, message.date)

def store_message(chat_id, sender_id, message, timestamp):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            sender_id INTEGER,
            message TEXT,
            timestamp TIMESTAMP
        )
    ''')
    cursor.execute('INSERT INTO messages (chat_id, sender_id, message, timestamp) VALUES (?, ?, ?, ?)',
                   (chat_id, sender_id, message, timestamp))
    conn.commit()
    conn.close()

async def main():
    # Ensure the client is connected and authorized
    await ensure_client_connected()
    # Replace 'your_group_or_chat_id' with the actual ID of the group or chat
    await fetch_messages(413064288)

with client:
    client.loop.run_until_complete(main())
