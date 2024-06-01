from dotenv import load_dotenv
import os
from telethon import TelegramClient, errors
import asyncio


load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")

# Create the client and connect using the existing session file
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

async def list_dialogs():
    # Ensure the client is connected and authorized
    await ensure_client_connected()

    try:
        # Get the list of dialogs
        dialogs = await client.get_dialogs()
        counter = 1
        for dialog in dialogs:
            entity = dialog.entity
            if hasattr(entity, 'title'):
                print(f'{counter}. Chat/Group: {entity.title} (ID: {entity.id})')
            else:
                print(f'{counter}. Chat: {entity.username} (ID: {entity.id})')
            counter += 1
    except errors.FloodWaitError as e:
        print(f'Rate limit exceeded. Waiting for {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
        await list_dialogs()
    except errors.BadMessageError as e:
        print(f'Bad message error: {e}')
    except errors.NewMessageError as e:
        print(f'New message error: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

with client:
    client.loop.run_until_complete(list_dialogs())
