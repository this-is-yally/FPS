#pylint: disable=no-member
#pylint: disable=undefined-variable

import requests
import re
import feedparser
import json
import sqlite3
import emoji
import logging
import asyncio
import keyboards as kb

from aiogram import Bot, types
logging.basicConfig(level=logging.INFO)
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bs4 import BeautifulSoup as BS
from config import TOKEN
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode



player_id = '' #ID игрока на сайте
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

name = ''

class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await Form.name.set()
    await message.reply("Привет!\nНапиши свой ник из Epic Games, и я отправлю твою статистику из Fortnite" + emoji.emojize(":envelope:"))

# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())
    
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

        headers = {"TRN-Api-Key": "api-key"}
        urll = 'https://api.fortnitetracker.com/v1/profile/all/'
        url = urll + data['name']
        r = requests.get(url, headers=headers)
        json_data = json.loads(r.text)

        print(r.status_code)
        player_name = json_data["epicUserHandle"]
        alltimewins = json_data['lifeTimeStats'][8]['value']
        alltimewinrate = json_data['lifeTimeStats'][9]['value']
        alltimekills = json_data['lifeTimeStats'][10]['value']
        alltimekd = json_data['lifeTimeStats'][11]['value']

        await message.reply("Никнейм: " + player_name + "\nПобед: " + alltimewins + "\nПроцент побед: " + alltimewinrate + "Убийств: " + alltimekills + "\nK/D: " + alltimekd)

    await state.finish()

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Создатель: @glob_glogab_galab" + emoji.emojize(":man_technologist:"))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)











