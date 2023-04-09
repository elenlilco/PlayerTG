# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from utils import LOGGER
from config import Config
from pyrogram import (
    Client, 
    filters
)
from utils import (
    chat_filter, 
    is_admin, 
    is_admin, 
    delete_messages, 
    recorder_settings,
    sync_to_db
)
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

admin_filter=filters.create(is_admin) 


@Client.on_message(filters.command(["record", "ریک", f"record@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def record_vc(bot, message):
    await message.reply("تنظیمه ضبط پلیرㅤㅤ ㅤ", reply_markup=(await recorder_settings()))
    await delete_messages([message])

@Client.on_message(filters.command(["rtitle", "تاریک", f"rtitle@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def recording_title(bot, message):
    m=await message.reply("در حال چک..")
    if " " in message.text:
        cmd, title = message.text.split(" ", 1)
    else:
        await m.edit("برای دادنه تایتل از این دستور استفاده کن: /rtitle")
        await delete_messages([message, m])
        return

    if Config.DATABASE_URI:
        await m.edit("دیتابیس پیدا شد، درحال تنظیم تایتل...") 
        if title == "False":
            await m.edit(f"با موفقیت تایتل شخصیتون پاکیده شد.")
            Config.RECORDING_TITLE=False
            await sync_to_db()
            await delete_messages([message, m])           
            return
        else:
            Config.RECORDING_TITLE=title
            await sync_to_db()
            await m.edit(f" {title} این تایتل با موفقیت تنظیم شد")
            await delete_messages([message, m])
            return
    else:
        if not Config.HEROKU_APP:
            buttons = [[InlineKeyboardButton('Heroku API_KEY', url='https://dashboard.heroku.com/account/applications/authorizations/new'), InlineKeyboardButton('🗑 Close', callback_data='close'),]]
            await m.edit(
                text="این ربات با هیروکو پیکربندی نشده.", 
                reply_markup=InlineKeyboardMarkup(buttons)) 
            await delete_messages([message])
            return     
        config = Config.HEROKU_APP.config()
        if title == "False":
            if "RECORDING_TITLE" in config:
                await m.edit(f"با موفقیت تایتل پاک شد، درحال ریست..")
                await delete_messages([message])
                del config["RECORDING_TITLE"]                
                config["RECORDING_TITLE"] = None
            else:
                await m.edit(f"درحال حاظر هم همین تنظیمه، چیزی تغییر نکرد")
                Config.RECORDING_TITLE=False
                await delete_messages([message, m])
        else:
            await m.edit(f"تایتل تغییر کرد به {title}, درحال ریست")
            await delete_messages([message])
            config["RECORDING_TITLE"] = title
