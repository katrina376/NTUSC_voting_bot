import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from time import sleep
import os

from modules import Congress

students = []
with open('meta/stu_id.txt', 'r') as f:
    for line in f:
        students.append(line.strip())

members = telepot.helper.SafeDict()  # thread-safe dict

polls = []

TOKEN = os.environ.get('BOT_TOKEN', '')

bot = Congress(TOKEN, members=members, polls=polls, students=students)
MessageLoop(bot).run_as_thread()

print('Listening ...')
# server.quit()
while 1:
    sleep(10)
