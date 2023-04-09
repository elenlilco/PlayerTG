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
    get_admins, 
    sync_to_db, 
    delete_messages,
    sudo_filter
)


@Client.on_message(filters.command(['vcpromote', 'نواپرو', f"vcpromote@{Config.BOT_USERNAME}"]) & sudo_filter)
async def add_admin(client, message):
    if message.reply_to_message:
        if message.reply_to_message.from_user.id is None:
            k = await message.reply("تو نمیتونی اینکارو کنی کصخل.")
            await delete_messages([message, k])
            return
        user_id=message.reply_to_message.from_user.id
        user=message.reply_to_message.from_user

    elif ' ' in message.text:
        c, user = message.text.split(" ", 1)
        if user.startswith("@"):
            user=user.replace("@", "")
            try:
                user=await client.get_users(user)
            except Exception as e:
                k=await message.reply(f"نمیتونم اینی ک میگیو پیدا کنم.\nارور: {e}")
                LOGGER.error(f"Unable to find the user - {e}", exc_info=True)
                await delete_messages([message, k])
                return
            user_id=user.id
        else:
            try:
                user_id=int(user)
                user=await client.get_users(user_id)
            except:
                k=await message.reply(f"یا ای دی عددی بده یا ای دی با @.")
                await delete_messages([message, k])
                return
    else:
        k=await message.reply("یا رو یکی ریپ بزن یا ای دی عددی بده یا ای دی با @.")
        await delete_messages([message, k])
        return
    if user_id in Config.ADMINS:
        k = await message.reply("همین الانشم ادمینه، کصخل.") 
        await delete_messages([message, k])
        return
    Config.ADMINS.append(user_id)
    k=await message.reply(f" {user.mention} ادمین شدش")
    await sync_to_db()
    await delete_messages([message, k])


@Client.on_message(filters.command(['vcdemote', 'نوادیمو', f"vcdemote@{Config.BOT_USERNAME}"]) & sudo_filter)
async def remove_admin(client, message):
    if message.reply_to_message:
        if message.reply_to_message.from_user.id is None:
            k = await message.reply("نمیتونی اینکارو بکنی کصخل.")
            await delete_messages([message, k])
            return
        user_id=message.reply_to_message.from_user.id
        user=message.reply_to_message.from_user
    elif ' ' in message.text:
        c, user = message.text.split(" ", 1)
        if user.startswith("@"):
            user=user.replace("@", "")
            try:
                user=await client.get_users(user)
            except Exception as e:
                k = await message.reply(f"متوجه نمیشم کیو میگی.\nارور: {e}")
                LOGGER.error(f"Unable to Locate user, {e}", exc_info=True)
                await delete_messages([message, k])
                return
            user_id=user.id
        else:
            try:
                user_id=int(user)
                user=await client.get_users(user_id)
            except:
                k = await message.reply(f"یا عای دی عددی بده یا عای دی با @.")
                await delete_messages([message, k])
                return
    else:
        k = await message.reply("یا ریپ بزن روش یا عای دی عددیشو بده یا عای دی با @.")
        await delete_messages([message, k])
        return
    if not user_id in Config.ADMINS:
        k = await message.reply("این از قبل هم ادمین نبود کصخل.")
        await delete_messages([message, k])
        return
    Config.ADMINS.remove(user_id)
    k = await message.reply(f" {user.mention} دیگه ادمین نیستش")
    await sync_to_db()
    await delete_messages([message, k])


@Client.on_message(filters.command(['refresh', 'رفرش' ,'پیکربندی', f"refresh@{Config.BOT_USERNAME}"]) & filters.user(Config.SUDO))
async def refresh_admins(client, message):
    Config.ADMIN_CACHE=False
    await get_admins(Config.CHAT)
    k = await message.reply("ادمین ها بروز شدن")
    await sync_to_db()
    await delete_messages([message, k])
