from dotenv import load_dotenv
import os
from telethon import TelegramClient, sync

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# Create the client and connect
client = TelegramClient('AIAST', api_id, api_hash)

# Start the client
client.start(phone=phone_number)

# This will send a code to your Telegram app, which you need to enter
if not client.is_user_authorized():
    client.send_code_request(phone_number)
    client.sign_in(phone_number, input('Enter the code: '))
