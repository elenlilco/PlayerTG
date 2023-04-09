# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from utils import LOGGER
from contextlib import suppress
from config import Config
import calendar
import pytz
from datetime import datetime
import asyncio
import os
from pyrogram.errors.exceptions.bad_request_400 import (
    MessageIdInvalid, 
    MessageNotModified
)
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from utils import (
    cancel_all_schedules,
    edit_config, 
    is_admin, 
    leave_call, 
    restart,
    restart_playout,
    stop_recording, 
    sync_to_db,
    update, 
    is_admin, 
    chat_filter,
    sudo_filter,
    delete_messages,
    seek_file
)
from pyrogram import (
    Client, 
    filters
)

IST = pytz.timezone(Config.TIME_ZONE)
if Config.DATABASE_URI:
    from utils import db

HOME_TEXT = "<b>هی  [{}](tg://user?id={}) 🙋‍♂️\n\nمن پلیر وویس چته کمپانی النلیلم.\nتو ضمینه ی پلیر های وویس چت، خدام حله؟.</b>"
admin_filter=filters.create(is_admin) 

@Client.on_message(filters.command(['start', f"start@{Config.BOT_USERNAME}"]))
async def start(client, message):
    if len(message.command) > 1:
        if message.command[1] == 'help':
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"پلی", callback_data='help_play'),
                        InlineKeyboardButton(f"تنظیمات", callback_data=f"help_settings"),
                        InlineKeyboardButton(f"ضبط", callback_data='help_record'),
                    ],
                    [
                        InlineKeyboardButton("زمانبندی", callback_data="help_schedule"),
                        InlineKeyboardButton("کنترلر", callback_data='help_control'),
                        InlineKeyboardButton("ادمین ها", callback_data="help_admin"),
                    ],
                    [
                        InlineKeyboardButton(f"متفرقه", callback_data='help_misc'),
                        InlineKeyboardButton("بستن", callback_data="close"),
                    ],
                ]
                )
            await message.reply("منوی راهنما.",
                reply_markup=reply_markup,
                disable_web_page_preview=True
                )
        elif 'sch' in message.command[1]:
            msg=await message.reply("چک کردنه زمانبندی ها..")
            you, me = message.command[1].split("_", 1)
            who=Config.SCHEDULED_STREAM.get(me)
            if not who:
                return await msg.edit("یچیزی یجایی بگا رفته.")
            del Config.SCHEDULED_STREAM[me]
            whom=f"{message.chat.id}_{msg.message_id}"
            Config.SCHEDULED_STREAM[whom] = who
            await sync_to_db()
            if message.from_user.id not in Config.ADMINS:
                return await msg.edit("OK da")
            today = datetime.now(IST)
            smonth=today.strftime("%B")
            obj = calendar.Calendar()
            thisday = today.day
            year = today.year
            month = today.month
            m=obj.monthdayscalendar(year, month)
            button=[]
            button.append([InlineKeyboardButton(text=f"{str(smonth)}  {str(year)}",callback_data=f"sch_month_choose_none_none")])
            days=["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"]
            f=[]
            for day in days:
                f.append(InlineKeyboardButton(text=f"{day}",callback_data=f"day_info_none"))
            button.append(f)
            for one in m:
                f=[]
                for d in one:
                    year_=year
                    if d < int(today.day):
                        year_ += 1
                    if d == 0:
                        k="\u2063"   
                        d="none"   
                    else:
                        k=d    
                    f.append(InlineKeyboardButton(text=f"{k}",callback_data=f"sch_month_{year_}_{month}_{d}"))
                button.append(f)
            button.append([InlineKeyboardButton("بستن", callback_data="schclose")])
            await msg.edit(f"روزه ماه رو انتخاب کن.\nامروز {thisday} {smonth} {year}. اگ همین الانو زمانبندی کنی ساله دیگ همین موقع پخش میشه {year+1}", reply_markup=InlineKeyboardMarkup(button))



        return
    buttons = [
        [
            InlineKeyboardButton('خالقم', url='https://t.me/ElenLiL'),
            InlineKeyboardButton('پورتال', url='https://t.me/ElenLiLBoT')
        ],
        [
            InlineKeyboardButton('👨🏼‍🦯 راهنما', callback_data='help_main'),
            InlineKeyboardButton('🗑 بستن', callback_data='close'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    k = await message.reply(HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)
    await delete_messages([message, k])



@Client.on_message(filters.command(["help", "راهنما", f"help@{Config.BOT_USERNAME}"]))
async def show_help(client, message):
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("پلی", callback_data='help_play'),
                InlineKeyboardButton("تنظیمات", callback_data=f"help_settings"),
                InlineKeyboardButton("ضبط", callback_data='help_record'),
            ],
            [
                InlineKeyboardButton("زمانبندی", callback_data="help_schedule"),
                InlineKeyboardButton("کنترلر", callback_data='help_control'),
                InlineKeyboardButton("ادمین ها", callback_data="help_admin"),
            ],
            [
                InlineKeyboardButton("متفرقه", callback_data='help_misc'),
                InlineKeyboardButton("کانفیگ", callback_data='help_env'),
                InlineKeyboardButton("بستن", callback_data="close"),
            ],
        ]
        )
    if message.chat.type != "private" and message.from_user is None:
        k=await message.reply(
            text="کصخل نمیشه",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"راهنما", url=f"https://telegram.dog/{Config.BOT_USERNAME}?start=help"),
                    ]
                ]
            ),)
        await delete_messages([message, k])
        return
    if Config.msg.get('help') is not None:
        await Config.msg['help'].delete()
    Config.msg['help'] = await message.reply_text(
        "منوی راهنما.",
        reply_markup=reply_markup,
        disable_web_page_preview=True
        )
    #await delete_messages([message])
@Client.on_message(filters.command(['repo', f"repo@{Config.BOT_USERNAME}"]))
async def repo_(client, message):
    buttons = [
        [
            InlineKeyboardButton('خالقم', url='https://t.me/ElenLiL'),
            InlineKeyboardButton('پورتال', url='https://t.me/ElenLiLBoT'),     
        ],
        [
            InlineKeyboardButton("کمپانی", url='https://t.me/ElenLiLBoT'),
            InlineKeyboardButton('🗑 بستن', callback_data='close'),
        ]
    ]
    await message.reply("<b>من خارق العاده ترین پلیره تلگرامم 🙃.</b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    await delete_messages([message])

@Client.on_message(filters.command(['restart', 'ریست' ,'ریستارت' ,'اپدیت', 'update', f"restart@{Config.BOT_USERNAME}", f"update@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def update_handler(client, message):
    if Config.HEROKU_APP:
        k = await message.reply("هیروکو پیدا شد، درحال اپدیت.")
        if Config.DATABASE_URI:
            msg = {"msg_id":k.message_id, "chat_id":k.chat.id}
            if not await db.is_saved("RESTART"):
                db.add_config("RESTART", msg)
            else:
                await db.edit_config("RESTART", msg)
            await sync_to_db()
    else:
        k = await message.reply("هیروکو پیدا نشد، درحال ریست.")
        if Config.DATABASE_URI:
            msg = {"msg_id":k.message_id, "chat_id":k.chat.id}
            if not await db.is_saved("RESTART"):
                db.add_config("RESTART", msg)
            else:
                await db.edit_config("RESTART", msg)
    try:
        await message.delete()
    except:
        pass
    await update()

@Client.on_message(filters.command(['logs', 'لاگ', f"logs@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def get_logs(client, message):
    m=await message.reply("چک کردن لاگ..")
    if os.path.exists("لاگ.txt"):
        await message.reply_document('لاگ.txt', caption="لاگه بات")
        await m.delete()
        await delete_messages([message])
    else:
        k = await m.edit("هیچ فایله لاگی پیدا نشد.")
        await delete_messages([message, k])

@Client.on_message(filters.command(['env', f"env@{Config.BOT_USERNAME}", "config", f"config@{Config.BOT_USERNAME}"]) & sudo_filter & chat_filter)
async def set_heroku_var(client, message):
    with suppress(MessageIdInvalid, MessageNotModified):
        m = await message.reply("چک کردن کانفیگ..")
        if " " in message.text:
            cmd, env = message.text.split(" ", 1)
            if "=" in env:
                var, value = env.split("=", 1)
            else:
                if env == "STARTUP_STREAM":
                    env_ = "STREAM_URL"
                elif env == "QUALITY":
                    env_ = "CUSTOM_QUALITY" 
                else:
                    env_ = env
                ENV_VARS = ["ADMINS", "SUDO", "CHAT", "LOG_GROUP", "STREAM_URL", "SHUFFLE", "ADMIN_ONLY", "REPLY_MESSAGE", 
                        "EDIT_TITLE", "RECORDING_DUMP", "RECORDING_TITLE", "IS_VIDEO", "IS_LOOP", "DELAY", "PORTRAIT", 
                        "IS_VIDEO_RECORD", "PTN", "CUSTOM_QUALITY"]
                if env_ in ENV_VARS:
                    await m.edit(f"ولیو برای این کانفیگ `{env}`  اینه `{getattr(Config, env_)}`")
                    await delete_messages([message])
                    return
                else:
                    await m.edit("این کانفیگ قابل قبول نیس.")
                    await delete_messages([message, m])
                    return     
            
        else:
            await m.edit("هیچ ولیویی برای کانفیگ مورد نظر ندادی کصخول.")
            await delete_messages([message, m])
            return

        if Config.DATABASE_URI and var in ["STARTUP_STREAM", "CHAT", "LOG_GROUP", "REPLY_MESSAGE", "DELAY", "RECORDING_DUMP", "QUALITY"]:      
            await m.edit("دیتابیس پیدا شد، درحال کانفیگ...")
            await asyncio.sleep(2)  
            if not value:
                await m.edit(f"هیچ ولیویی برای کانفیگ پیدا نشد، لطفن کانفیگ رو پاک کنید {var}.")
                await asyncio.sleep(2)
                if var in ["STARTUP_STREAM", "CHAT", "DELAY"]:
                    await m.edit("این کانفیگ ها ریشه این وقابل پاک شدن نیستن.")
                    await delete_messages([message, m]) 
                    return
                await edit_config(var, False)
                await m.edit(f"کانفیگ با موفقیت پاک شد {var}")
                await delete_messages([message, m])           
                return
            else:
                if var in ["CHAT", "LOG_GROUP", "RECORDING_DUMP", "QUALITY"]:
                    try:
                        value=int(value)
                    except:
                        if var == "QUALITY":
                            if not value.lower() in ["low", "medium", "high"]:
                                await m.edit("فقط میتونی بین ۱۰ تا ۱۰۰ رو انتخاب کنی.")
                                await delete_messages([message, m])
                                return
                            else:
                                value = value.lower()
                                if value == "high":
                                    value = 100
                                elif value == "medium":
                                    value = 66.9
                                elif value == "low":
                                    value = 50
                        else:
                            await m.edit("باید بهم ای دی عددیه گپو بدی.")
                            await delete_messages([message, m])
                            return
                    if var == "CHAT":
                        await leave_call()
                        Config.ADMIN_CACHE=False
                        if Config.IS_RECORDING:
                            await stop_recording()
                        await cancel_all_schedules()
                        Config.CHAT=int(value)
                        await restart()
                    await edit_config(var, int(value))
                    if var == "QUALITY":
                        if Config.CALL_STATUS:
                            data=Config.DATA.get('FILE_DATA')
                            if not data \
                                or data.get('dur', 0) == 0:
                                await restart_playout()
                                return
                            k, reply = await seek_file(0)
                            if k == False:
                                await restart_playout()
                    await m.edit(f"با موفقیت این کانفیگ {var} با این ولیو {value} تنظیم شد")
                    await delete_messages([message, m])
                    return
                else:
                    if var == "STARTUP_STREAM":
                        Config.STREAM_SETUP=False
                    await edit_config(var, value)
                    await m.edit(f"با موفقیت این کانفیگ {var} با این ولیو {value} تنظیم شد")
                    await delete_messages([message, m])
                    await restart_playout()
                    return
        else:
            if not Config.HEROKU_APP:
                buttons = [[InlineKeyboardButton('Heroku API_KEY', url='https://dashboard.heroku.com/account/applications/authorizations/new'), InlineKeyboardButton('🗑 بستن', callback_data='close'),]]
                await m.edit(
                    text="هیچ هیروکویی پیدا نشد این دستور نیاز ب هیروکو داره.\n\n1. <code>HEROKU_API_KEY</code>: ای پی عایه اکانته هیروکوی شما.\n2. <code>HEROKU_APP_NAME</code>: اسم برنامه ی هیروکوی شما.", 
                    reply_markup=InlineKeyboardMarkup(buttons)) 
                await delete_messages([message])
                return     
            config = Config.HEROKU_APP.config()
            if not value:
                await m.edit(f"همچین ولیویی قابل قبول نیس لطفن این کانفیگ رو پاک کنید {var}.")
                await asyncio.sleep(2)
                if var in ["STARTUP_STREAM", "CHAT", "DELAY", "API_ID", "API_HASH", "BOT_TOKEN", "SESSION_STRING", "ADMINS"]:
                    await m.edit("این کانفیگ ها ریشه این و قابله پاک شدن نیستن.")
                    await delete_messages([message, m])
                    return
                if var in config:
                    await m.edit(f"این کانفیگ {var} با موفقیت پاک شد")
                    await asyncio.sleep(2)
                    await m.edit("حالا درحاله ریست پلیر برای اعمال تغییرات....")
                    if Config.DATABASE_URI:
                        msg = {"msg_id":m.message_id, "chat_id":m.chat.id}
                        if not await db.is_saved("RESTART"):
                            db.add_config("RESTART", msg)
                        else:
                            await db.edit_config("RESTART", msg)
                    del config[var]                
                    config[var] = None               
                else:
                    k = await m.edit(f"هیچ کانفیگی با این اسم {var} پیدا نشد، پ چیزیم تغییر نکرد.")
                    await delete_messages([message, k])
                return
            if var in config:
                await m.edit(f"حله تغییر پیدا کرد به {value}")
            else:
                await m.edit(f"کانفیگ وجود نداشت و الان نصب شد.")
            await asyncio.sleep(2)
            await m.edit(f"این کانفیگ {var} با موفقیت با این ولیو {value}, تنظیم شد و حالا برای اعمال تغییرات ربات رو ریست میکنیم...")
            if Config.DATABASE_URI:
                msg = {"msg_id":m.message_id, "chat_id":m.chat.id}
                if not await db.is_saved("RESTART"):
                    db.add_config("RESTART", msg)
                else:
                    await db.edit_config("RESTART", msg)
            config[var] = str(value)




