# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from utils import LOGGER
try:
   import os
   import heroku3
   from dotenv import load_dotenv
   from ast import literal_eval as is_enabled

except ModuleNotFoundError:
    import os
    import sys
    import subprocess
    file=os.path.abspath("requirements.txt")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', file, '--upgrade'])
    os.execl(sys.executable, sys.executable, *sys.argv)


class Config:
    #Telegram API Stuffs
    load_dotenv()  # load enviroment variables from .env file
    ADMIN = os.environ.get("ADMINS", '')
    SUDO = [int(admin) for admin in (ADMIN).split()] # Exclusive for heroku vars configuration.
    ADMINS = [int(admin) for admin in (ADMIN).split()] #group admins will be appended to this list.
    API_ID = int(os.environ.get("API_ID", ''))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")     
    SESSION = os.environ.get("SESSION_STRING", "")

    #Stream Chat and Log Group
    CHAT = int(os.environ.get("CHAT", ""))
    LOG_GROUP=os.environ.get("LOG_GROUP", "")

    #Stream 
    STREAM_URL=os.environ.get("STARTUP_STREAM", "https://www.youtube.com/watch?v=zcrUCvBD16k")
   
    #Database
    DATABASE_URI=os.environ.get("DATABASE_URI", None)
    DATABASE_NAME=os.environ.get("DATABASE_NAME", "VCPlayerBot")


    #heroku
    API_KEY=os.environ.get("HEROKU_API_KEY", None)
    APP_NAME=os.environ.get("HEROKU_APP_NAME", None)


    #Optional Configuration
    SHUFFLE=is_enabled(os.environ.get("SHUFFLE", 'True'))
    ADMIN_ONLY=is_enabled(os.environ.get("ADMIN_ONLY", "False"))
    REPLY_MESSAGE=os.environ.get("REPLY_MESSAGE", False)
    EDIT_TITLE = os.environ.get("EDIT_TITLE", True)
    #others
    
    RECORDING_DUMP=os.environ.get("RECORDING_DUMP", False)
    RECORDING_TITLE=os.environ.get("RECORDING_TITLE", False)
    TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Kolkata")    
    IS_VIDEO=is_enabled(os.environ.get("IS_VIDEO", 'True'))
    IS_LOOP=is_enabled(os.environ.get("IS_LOOP", 'True'))
    DELAY=int(os.environ.get("DELAY", '10'))
    PORTRAIT=is_enabled(os.environ.get("PORTRAIT", 'False'))
    IS_VIDEO_RECORD=is_enabled(os.environ.get("IS_VIDEO_RECORD", 'True'))
    DEBUG=is_enabled(os.environ.get("DEBUG", 'False'))
    PTN=is_enabled(os.environ.get("PTN", "False"))

    #Quality vars
    E_BITRATE=os.environ.get("BITRATE", False)
    E_FPS=os.environ.get("FPS", False)
    CUSTOM_QUALITY=os.environ.get("QUALITY", "100")

    #Search filters for cplay
    FILTERS =  [filter.lower() for filter in (os.environ.get("FILTERS", "video document")).split(" ")]


    #Dont touch these, these are not for configuring player
    GET_FILE={}
    DATA={}
    STREAM_END={}
    SCHEDULED_STREAM={}
    DUR={}
    msg = {}

    SCHEDULE_LIST=[]
    playlist=[]
    CONFIG_LIST = ["ADMINS", "IS_VIDEO", "IS_LOOP", "REPLY_PM", "ADMIN_ONLY", "SHUFFLE", "EDIT_TITLE", "CHAT", 
    "SUDO", "REPLY_MESSAGE", "STREAM_URL", "DELAY", "LOG_GROUP", "SCHEDULED_STREAM", "SCHEDULE_LIST", 
    "IS_VIDEO_RECORD", "IS_RECORDING", "WAS_RECORDING", "RECORDING_TITLE", "PORTRAIT", "RECORDING_DUMP", "HAS_SCHEDULE", 
    "CUSTOM_QUALITY"]

    STARTUP_ERROR=None

    ADMIN_CACHE=False
    CALL_STATUS=False
    YPLAY=False
    YSTREAM=False
    CPLAY=False
    STREAM_SETUP=False
    LISTEN=False
    STREAM_LINK=False
    IS_RECORDING=False
    WAS_RECORDING=False
    PAUSE=False
    MUTED=False
    HAS_SCHEDULE=None
    IS_ACTIVE=None
    VOLUME=100
    CURRENT_CALL=None
    BOT_USERNAME=None
    USER_ID=None

    if LOG_GROUP:
        LOG_GROUP=int(LOG_GROUP)
    else:
        LOG_GROUP=None
    if not API_KEY or \
       not APP_NAME:
       HEROKU_APP=None
    else:
       HEROKU_APP=heroku3.from_key(API_KEY).apps()[APP_NAME]


    if EDIT_TITLE in ["NO", 'False']:
        EDIT_TITLE=False
        LOGGER.info("Title Editing turned off")
    if REPLY_MESSAGE:
        REPLY_MESSAGE=REPLY_MESSAGE
        REPLY_PM=True
        LOGGER.info("Reply Message Found, Enabled PM MSG")
    else:
        REPLY_MESSAGE=False
        REPLY_PM=False

    if E_BITRATE:
       try:
          BITRATE=int(E_BITRATE)
       except:
          LOGGER.error("Invalid bitrate specified.")
          E_BITRATE=False
          BITRATE=48000
       if not BITRATE >= 48000:
          BITRATE=48000
    else:
       BITRATE=48000
    
    if E_FPS:
       try:
          FPS=int(E_FPS)
       except:
          LOGGER.error("Invalid FPS specified")
          E_FPS=False
       if not FPS >= 30:
          FPS=30
    else:
       FPS=30
    try:
       CUSTOM_QUALITY=int(CUSTOM_QUALITY)
       if CUSTOM_QUALITY > 100:
          CUSTOM_QUALITY = 100
          LOGGER.warning("maximum quality allowed is 100, invalid quality specified. Quality set to 100")
       elif CUSTOM_QUALITY < 10:
          LOGGER.warning("Minimum Quality allowed is 10., Qulaity set to 10")
          CUSTOM_QUALITY = 10
       if  66.9  < CUSTOM_QUALITY < 100:
          if not E_BITRATE:
             BITRATE=48000
       elif 50 < CUSTOM_QUALITY < 66.9:
          if not E_BITRATE:
             BITRATE=36000
       else:
          if not E_BITRATE:
             BITRATE=24000
    except:
       if CUSTOM_QUALITY.lower() == 'high':
          CUSTOM_QUALITY=100
       elif CUSTOM_QUALITY.lower() == 'medium':
          CUSTOM_QUALITY=66.9
       elif CUSTOM_QUALITY.lower() == 'low':
          CUSTOM_QUALITY=50
       else:
          LOGGER.warning("Invalid QUALITY specified.Defaulting to High.")
          CUSTOM_QUALITY=100



    #help strings 
    PLAY_HELP="""
__از گزینه ها میتونی استفاده کنی__

1. پلی کردن مدیا با لینک یوتوب.
دستور: **/play**
__میتونی روی ی لینکه یوتوب ریپ بزنی یا جلوی دستور بنویسیش.__

2. پلی کردنه فایل تلگرام.
دستور: **/play**
__ریپ بزن رو فایلی ک میخای پلیش .__
نکته: __در هر دو صورت اگ میخای چیزی بلافاصله پلی بشه باید بنویسی /fplay.__

3. پلی از طریق پلی لیست یوتوب
دستور: **/yplay**
__ابتدا از طریق این ربات ها پلی لیست رو بگیر @GetPlaylistBot یا @DumpPlaylist بعد ریپ بزن روی فایل پلی لیست.__

4. پخش زنده
دستور: **/stream**
__لینکه پخش زنده رو جلوی دستور بنویس.__

5. استفاده از پلی لیست شخصی.
دستور: **/import**
__روی فایل پلی لیست ریپ بزن . __

6. پلی از چنل
دستور: **/cplay**
__عای دی عددی چنل رو جلو دستور بنویس، اگ چنل شخصیه باید ربات ادمینش باشه اگ شخصی نیستو عمومیه ربات ادمینش هم نباشه روال میشه، بطور کلی میتونی فیلتر هم تنظیم ک دوس داری چ تایپ فایلی رو از چنل پلی کنه ربات__
"""
    SETTINGS_HELP="""
**با دستور زیر میتونی تنظیم کنی رباتو**

🔹دستور: **/settings**

🔹تنظیماته در دسترس:

**پلیر مود** -  __از طریق این اپشن میتونی تبدیل کنی رباتو به پلیره ۲۴/۷.__

**ویدیو فعال** -  __از طریق این اپشن میتونی تنظیم کنی ک فقط صدا پلی بشه یا ن ویدیو هم پلی بشه.__

**فقط ادمین** - __از طریق این اپشن میتونی تعیین کنی ک همه ب دستورای ربات دسترسی داشته باشن یا فقط ادمینا دسترسی داشتع باشن.__

**تغییر تایتل** - __با این اپشن میتونی تعیین کنی ک هر فایلی ک توسطه ربات پلی شد، تایتله وویس چت هم اسمه فایل بشه یا ن هیچ تغییری نکنه.__

**مود درهم** - __با این گزینه میتونی تنظیم کنی ک قروقاطی فایل های پلی لیست پلی بشن__

**ریپلای** - __با این اپشن میتونی تعیین کنی ک هرکی رفت پی وی رباته دستیار، رباته دستیار جوابشو بده یا تخمش بگیره.__

"""
    SCHEDULER_HELP="""
__از طریق این اپشن میتونی فایل هارو با زمانبندی پلی کنی __

دستور: **/schedule**

__چیزی ک میخای رو روش ریپ بزن یا جلوی دستور بنویس__

دستور: **/slist**
__دیدنه لیست زمانبندی های موجود.__

دستور: **/cancel**
__کنسل کردنه یک زمانبندی با کد عان__

دستور: **/cancelall**
__کنسل کردنه تمام زمانبندی ها__
"""
    RECORDER_HELP="""
__ضبط از ۱ تا چهار ساعت برای وویس چت با تصویر توسطه ربات__

دستور: **/record**

تنظیماته در دسترس:
1. ضبط ویدیو: __ضبط ویدیویی در وویس چت.__

2. ابعاد ویدیو: __میتونی حالته ضبط رو از بین عمودی و افقی انتخاب کنی__

3. تایتله شخصی برای ضبط: __میتونید با دستور /rtitle ، یک تایتله شخصی بدید ب ضبطتون__

4. دیتابیس ضبط: __میتونید ب سادگی با کانفیگه ربات، به ربات ی چنل معرفی کنید ک خودمار هرچی ضبط کرد بره تو اون چنل.__

⚠️ اگه ضبطی رو با ربات شروع کردید، با ربات هم باید تمومش کنید.

"""

    CONTROL_HELP="""
__کنترلر به شما کمک میکنه ک مدیای پخش شده رو راحت مدیریت کنید__
1. رد کردن.
دستور: **/skip**
__راحت میتونی با این دستور بزنی ی موزیک بره بعدی.__

2. استوپ کردن.
دستور: **/pause**

3. از سرگیری.
دستور: **/resume**

4. تغییر ولوم.
دستور: **/volume**
__جلوی دستور باید عددی بین ۱ تا ۱۰۰ بنویسی.__

5. خروج از وویس چت.
دستور: **/leave**

6. پلی لیست درهم.
دستور: **/shuffle**

7. قطع کامل ی فایل درحال پخش
دستور: **/clearplaylist**

8. جلو زدنه پخش.
دستور: **/seek**
__با این دستور میتونی بگی چن ثانیه فایل درحال پخش بره جلو.__

9. سکوت پلیر.
دستور: **/vcmute**

10. لغو سکوت پلیر.
دستور : **/vcunmute**

11. دیدنه پلی لیست.
دستور: **/playlist** 
__برای نمایش پلی لیست ب همرا کنترلر از این دستور استفاده کنید: /player__
"""

    ADMIN_HELP="""
__از طریق این اپشن میتونید ادمین ها رو شخصی سازی کنید__

دستور: **/vcpromote**
__اضافه کردن یک شخص ب ادمین های ربات.__

دستور: **/vcdemote**
__لغو ادمین کردن شخصی__

دستور: **/refresh**
__هماهنگ سازیه ادمین های کپ با ادمین های ربات__
"""

    MISC_HELP="""
دستور: **/export**
__از طریق این دستور میتونید پلی لیست شخصی بسازید__

دستور : **/logs**
__از طریق این دستور میتونید اتفاقاتی ک اخیرن توی کدنویسی و ترمینال ربات رخ داده رو ببینید__
 
دستور : **/env**
__از طریق این دستور میتونید کانفیگ کنید رباتو، بدون اینکه وارد کدنویسیش بشید__

دستور: **/config**

دستور: **/update**
__اپدیت کردنه ربات با اخرین تغییرات__

نکته: __شما میتونید ب سادگی با اد کردنه ربات به ی گپ دیگه، ربات رو اختصاصی کانفیگه اون گپ کنید__

"""
    ENV_HELP="""
**این ها دستورای کانفیگ هستن**


**کانفیگ های ریشه ای**

1. `API_ID`

2. `API_HASH`

3. `BOT_TOKEN`

4. `SESSION_STRING`

5. `CHAT`

6. `STARTUP_STREAM`

**کانفیگ های اختیاری**

1. `DATABASE_URI`

2. `HEROKU_API_KEY`

3. `HEROKU_APP_NAME`

4. `FILTERS`

**الباقی کانفیگ های اختیاری**
1. `LOG_GROUP`

2. `ADMINS`

3. `REPLY_MESSAGE`

4. `ADMIN_ONLY`

5. `DATABASE_NAME`

6. `SHUFFLE`

7. `EDIT_TITLE`

8. `RECORDING_DUMP`

9. `RECORDING_TITLE`

10. `TIME_ZONE`

11. `IS_VIDEO_RECORD`

12. `IS_LOOP`

13. `IS_VIDEO`

14. `PORTRAIT`

15. `DELAY`

16. `QUALITY`

17. `BITRATE`

18. `FPS`

"""
