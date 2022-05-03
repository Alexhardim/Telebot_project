import sqlite3, logging, random, smtplib, time, requests, asyncio
import threading
import datetime
from aiogram import Bot, Dispatcher, executor, types
from filter import IsAdminFilter
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from SonoffBasic.sonoff import Sonoff
from twisted.internet import task, reactor
import devises
import threading

Token = '######'
GROUP_ID = #####
username = 'alexhardim@gmail.com'
password = '######'
region='eu'
api_region = 'eu'
timezone='EU/Moscow'
user_apikey = 'None'
bearer_token = 'None'
grace_period = '600'
msg = 0
t = False
qwe = True
config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = OWM('8fda0c29d00635804412f9ec5ff7acb8', config_dict)
c = 0

ewelink = False

register = False
cod = False
user = 0
dont_reg = []
r = []
gm = []
con = sqlite3.connect("Telebot.sqlite")
cur = con.cursor()
result = cur.execute("""SELECT
       TELEGRAM
  FROM register;""").fetchall()
result2 = cur.execute("""SELECT
       Email
  FROM register;""").fetchall()
