# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from utils import LOGGER
from youtube_search import YoutubeSearch
from contextlib import suppress
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from datetime import datetime
from pyrogram import filters
from config import Config
from PTN import parse
import re
from utils import (
    add_to_db_playlist, 
    clear_db_playlist, 
    delete_messages, 
    download, 
    get_admins, 
    get_duration,
    is_admin, 
    get_buttons, 
    get_link, 
    import_play_list, 
    is_audio, 
    leave_call, 
    play, 
    get_playlist_str, 
    send_playlist, 
    shuffle_playlist, 
    start_stream, 
    stream_from_link, 
    chat_filter,
    c_play,
    is_ytdl_supported
)
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
    )
from pyrogram.errors import (
    MessageIdInvalid, 
    MessageNotModified,
    UserNotParticipant,
    PeerIdInvalid,
    ChannelInvalid
    )
from pyrogram import (
    Client, 
    filters
    )


admin_filter=filters.create(is_admin) 

@Client.on_message(filters.command(["play", "پلی", "fplay", f"play@{Config.BOT_USERNAME}", f"fplay@{Config.BOT_USERNAME}"]) & chat_filter)
async def add_to_playlist(_, message: Message):
    with suppress(MessageIdInvalid, MessageNotModified):
        admins = await get_admins(Config.CHAT)
        if Config.ADMIN_ONLY:
            if not (message.from_user is None and message.sender_chat or message.from_user.id in admins):
                k=await message.reply_sticker("CAADBQADsQIAAtILIVYld1n74e3JuQI")
                await delete_messages([message, k])
                return
        type=""
        yturl=""
        ysearch=""
        url=""
        if message.command[0] == "fplay":
            if not (message.from_user is None and message.sender_chat or message.from_user.id in admins):
                k=await message.reply("این دستور مخصوصه ادمیناس کونی.")
                await delete_messages([message, k])
                return
        msg = await message.reply_text("⚡️ **چک کردن ورودی..**")
        if message.reply_to_message and message.reply_to_message.video:
            await msg.edit("⚡️ **چک کردن مدیای تلگرام...**")
            type='video'
            m_video = message.reply_to_message.video       
        elif message.reply_to_message and message.reply_to_message.document:
            await msg.edit("⚡️ **چک کردن مدیای تلگرام...**")
            m_video = message.reply_to_message.document
            type='video'
            if not "video" in m_video.mime_type:
                return await msg.edit("این فایل نامعتبره")
        elif message.reply_to_message and message.reply_to_message.audio:
            #if not Config.IS_VIDEO:
                #return await message.reply("پلی کردن صدای فایل در دسترسه.")
            await msg.edit("⚡️ **چک کردن مدیای تلگرام...**")
            type='audio'
            m_video = message.reply_to_message.audio       
        else:
            if message.reply_to_message and message.reply_to_message.text:
                query=message.reply_to_message.text
            elif " " in message.text:
                text = message.text.split(" ", 1)
                query = text[1]
            else:
                await msg.edit("هیچی بهم ندادی ک پلی کنم گاگول.")
                await delete_messages([message, msg])
                return
            regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
            match = re.match(regex,query)
            if match:
                type="youtube"
                yturl=query
            elif query.startswith("http"):
                try:
                    has_audio_ = await is_audio(query)
                except:
                    has_audio_ = False
                    LOGGER.error("Unable to get Audio properties within time.")
                if has_audio_:
                    try:
                        dur=await get_duration(query)
                    except:
                        dur=0
                    if dur == 0:
                        await msg.edit("این پخش زنده محصوب میشه از این دستور استفاده کن: /stream.")
                        await delete_messages([message, msg])
                        return 
                    type="direct"
                    url=query
                else:
                    if is_ytdl_supported(query):
                        type="ytdl_s"
                        url=query
                    else:
                        await msg.edit("لینک نامعتبره.")
                        await delete_messages([message, msg])
                        return
            else:
                type="query"
                ysearch=query
        if not message.from_user is None:
            user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            user_id = message.from_user.id
        else:
            user="Anonymous"
            user_id = "anonymous_admin"
        now = datetime.now()
        nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
        if type in ["video", "audio"]:
            if type == "audio":
                if m_video.title is None:
                    if m_video.file_name is None:
                        title_ = "Music"
                    else:
                        title_ = m_video.file_name
                else:
                    title_ = m_video.title
                if m_video.performer is not None:
                    title = f"{m_video.performer} - {title_}"
                else:
                    title=title_
                unique = f"{nyav}_{m_video.file_size}_audio"
            else:
                title=m_video.file_name
                unique = f"{nyav}_{m_video.file_size}_video"
                if Config.PTN:
                    ny = parse(title)
                    title_ = ny.get("title")
                    if title_:
                        title = title_
            file_id=m_video.file_id
            if title is None:
                title = 'Music'
            data={1:title, 2:file_id, 3:"telegram", 4:user, 5:unique}
            if message.command[0] == "fplay":
                pla = [data] + Config.playlist
                Config.playlist = pla
            else:
                Config.playlist.append(data)
            await add_to_db_playlist(data)        
            await msg.edit("به پلی لیست اضافه شد")
        elif type in ["youtube", "query", "ytdl_s"]:
            if type=="youtube":
                await msg.edit("⚡️ **بارگیری از یوتوب...**")
                url=yturl
            elif type=="query":
                try:
                    await msg.edit("⚡️ **بارگیری از یوتوب...**")
                    ytquery=ysearch
                    results = YoutubeSearch(ytquery, max_results=1).to_dict()
                    url = f"https://youtube.com{results[0]['url_suffix']}"
                    title = results[0]["title"][:40]
                except Exception as e:
                    await msg.edit(
                        "پیداش نکردم.\nمیتونی از حالته اینلاین هم استفاده کنیا.."
                    )
                    LOGGER.error(str(e), exc_info=True)
                    await delete_messages([message, msg])
                    return
            elif type == "ytdl_s":
                url=url
            else:
                return
            ydl_opts = {
                "quite": True,
                "geo-bypass": True,
                "nocheckcertificate": True
            }
            ydl = YoutubeDL(ydl_opts)
            try:
                info = ydl.extract_info(url, False)
            except Exception as e:
                LOGGER.error(e, exc_info=True)
                await msg.edit(
                    f"خطا تو دانلود از یوتوب ❌\nارور:- {e}"
                    )
                LOGGER.error(str(e))
                await delete_messages([message, msg])
                return
            if type == "ytdl_s":
                title = "Music"
                try:
                    title = info['title']
                except:
                    pass
            else:
                title = info["title"]
                if info['duration'] is None:
                    await msg.edit("این پخش زنده محصوب میشه باید از دستور /stream استفاده کنی.")
                    await delete_messages([message, msg])
                    return 
            data={1:title, 2:url, 3:"youtube", 4:user, 5:f"{nyav}_{user_id}"}
            if message.command[0] == "fplay":
                pla = [data] + Config.playlist
                Config.playlist = pla
            else:
                Config.playlist.append(data)
            await add_to_db_playlist(data)
            await msg.edit(f"[{title}]({url}) به پلی لیست اضافه شد", disable_web_page_preview=True)
        elif type == "direct":
            data={1:"Music", 2:url, 3:"url", 4:user, 5:f"{nyav}_{user_id}"}
            if message.command[0] == "fplay":
                pla = [data] + Config.playlist
                Config.playlist = pla
            else:
                Config.playlist.append(data)
            await add_to_db_playlist(data)        
            await msg.edit("لینک ب پلی لیست افزوده شد")
        if not Config.CALL_STATUS \
            and len(Config.playlist) >= 1:
            await msg.edit("درحال دانلود...")
            await download(Config.playlist[0], msg)
            await play()
        elif (len(Config.playlist) == 1 and Config.CALL_STATUS):
            await msg.edit("درحال دانلود...")
            await download(Config.playlist[0], msg)  
            await play()
        elif message.command[0] == "fplay":
            await msg.edit("درحال دانلود...")
            await download(Config.playlist[0], msg)  
            await play()
        else:
            await send_playlist()  
        await msg.delete()
        pl=await get_playlist_str()
        if message.chat.type == "private":
            await message.reply(pl, reply_markup=await get_buttons() ,disable_web_page_preview=True)       
        elif not Config.LOG_GROUP and message.chat.type == "supergroup":
            if Config.msg.get('playlist') is not None:
                await Config.msg['playlist'].delete()
            Config.msg['playlist']=await message.reply(pl, disable_web_page_preview=True, reply_markup=await get_buttons())    
            await delete_messages([message])  
        for track in Config.playlist[:2]:
            await download(track)


@Client.on_message(filters.command(["leave", "بیرون", f"leave@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def leave_voice_chat(_, m: Message):
    if not Config.CALL_STATUS:        
        k=await m.reply("توی هیچ وویس چتی نیستم.")
        await delete_messages([m, k])
        return
    await leave_call()
    k=await m.reply("ع وویس چت اومدم بیرون.")
    await delete_messages([m, k])



@Client.on_message(filters.command(["shuffle", "درهم", f"shuffle@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def shuffle_play_list(client, m: Message):
    if not Config.CALL_STATUS:
        k = await m.reply("توی هیچ وویس چتی نیستم.")
        await delete_messages([m, k])
        return
    else:
        if len(Config.playlist) > 2:
            k=await m.reply_text(f"پلی لیست درهم شد.")
            await shuffle_playlist()
            await delete_messages([m, k])            
        else:
            k=await m.reply_text(f"پلی لیستی ک کمتر از ۳ تا مدیا داشته باشه رو نمیتونی درهم کنی.")
            await delete_messages([m, k])


@Client.on_message(filters.command(["clearplaylist", "نوابسه", f"clearplaylist@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def clear_play_list(client, m: Message):
    if not Config.playlist:
        k = await m.reply("پلی لیست خالیه.")  
        await delete_messages([m, k])
        return
    Config.playlist.clear()
    k=await m.reply_text(f"پلی لیست خالی شد.")
    await clear_db_playlist(all=True)
    if Config.IS_LOOP \
        and not (Config.YPLAY or Config.CPLAY):
        await start_stream()
    else:
        await leave_call()
    await delete_messages([m, k])



@Client.on_message(filters.command(["cplay", "چپلی", f"cplay@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def channel_play_list(client, m: Message):
    with suppress(MessageIdInvalid, MessageNotModified):
        k=await m.reply("تنظیم برای پخش از چنل..")
        if " " in m.text:
            you, me = m.text.split(" ", 1)
            if me.startswith("-100"):
                try:
                    me=int(me)
                except:
                    await k.edit("عای دی عددی اشتباهه")
                    await delete_messages([m, k])
                    return
                try:
                    await client.get_chat_member(int(me), Config.USER_ID)
                except (ValueError, PeerIdInvalid, ChannelInvalid):
                    LOGGER.error(f"Given channel is private and @{Config.BOT_USERNAME} is not an admin over there.", exc_info=True)
                    await k.edit(f"این چنل خصوصیه و رباته @{Config.BOT_USERNAME} ادمین نیس توش.")
                    await delete_messages([m, k])
                    return
                except UserNotParticipant:
                    LOGGER.error("Given channel is private and USER account is not a member of channel.")
                    await k.edit("این چنل خصوصیه و دستیار ربات توش ادمین نیس.")
                    await delete_messages([m, k])
                    return
                except Exception as e:
                    LOGGER.error(f"Errors occured while getting data abount channel - {e}", exc_info=True)
                    await k.edit(f"یچیزی مشکل داره- {e}")
                    await delete_messages([m, k])
                    return
                await k.edit("درحال پردازش فایل های چنل، بسته به تعداد فایل های چنل، زمان سپری میشه.")
                st, msg = await c_play(me)
                if st == False:
                    await m.edit(msg)
                else:
                    await k.edit(f"این {msg} فایل ها ب پلی لیست اضافه شدن.")
            elif me.startswith("@"):
                me = me.replace("@", "")
                try:
                    chat=await client.get_chat(me)
                except Exception as e:
                    LOGGER.error(f"Errors occured while fetching info about channel - {e}", exc_info=True)
                    await k.edit(f"حین گرفتنه فایل ها از چنل خطا رخ داد - {e}")
                    await delete_messages([m, k])
                    return
                await k.edit("پردازش فایل ها از چنل، بسته به تعداد فایل های چنل، زمان نیاز داره.")
                st, msg=await c_play(me)
                if st == False:
                    await k.edit(msg)
                    await delete_messages([m, k])
                else:
                    await k.edit(f"این {msg} فایل ها از چنل {chat.title} به پلی لیست")
                    await delete_messages([m, k])
            else:
                await k.edit("عای دی عددیه چنلی ک دادی اشتباهه.")
                await delete_messages([m, k])
        else:
            await k.edit("اصن بهم هیچ چنلی ندادی گوساله.")
            await delete_messages([m, k])



@Client.on_message(filters.command(["yplay", "یوپلی", f"yplay@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def yt_play_list(client, m: Message):
    with suppress(MessageIdInvalid, MessageNotModified):
        if m.reply_to_message is not None and m.reply_to_message.document:
            if m.reply_to_message.document.file_name != "YouTube_PlayList.json":
                k=await m.reply("فایل پلی لیستی ک بهم دادی نامعتبره.")
                await delete_messages([m, k])
                return
            ytplaylist=await m.reply_to_message.download()
            status=await m.reply("درحال پردازش اطلاعات پلی لیست.")
            n=await import_play_list(ytplaylist)
            if not n:
                await status.edit("حین پردازش اطلاعات از پلی لیست، خطا رخ داد.")
                await delete_messages([m, status])
                return
            if Config.SHUFFLE:
                await shuffle_playlist()
            pl=await get_playlist_str()
            if m.chat.type == "private":
                await status.edit(pl, disable_web_page_preview=True, reply_markup=await get_buttons())        
            elif not Config.LOG_GROUP and m.chat.type == "supergroup":
                if Config.msg.get("playlist") is not None:
                    await Config.msg['playlist'].delete()
                Config.msg['playlist']=await status.edit(pl, disable_web_page_preview=True, reply_markup=await get_buttons())
                await delete_messages([m])
            else:
                await delete_messages([m, status])
        else:
            k=await m.reply("هیچ فایل پلی لیستی بهم ندادی گوساله.")
            await delete_messages([m, k])


@Client.on_message(filters.command(["stream", "استریم", f"stream@{Config.BOT_USERNAME}"]) & admin_filter & chat_filter)
async def stream(client, m: Message):
    with suppress(MessageIdInvalid, MessageNotModified):
        msg=await m.reply("چک کردنه ورودی.")
        if m.reply_to_message and m.reply_to_message.text:
            link=m.reply_to_message.text
        elif " " in m.text:
            text = m.text.split(" ", 1)
            link = text[1]
        else:
            k = await msg.edit("لینکه استریمو باید بهم بدی!")
            await delete_messages([m, k])
            return
        regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
        match = re.match(regex,link)
        if match:
            stream_link=await get_link(link)
            if not stream_link:
                k = await msg.edit("این لینک نامعتبره.")
                await delete_messages([m, k])
                return
        else:
            stream_link=link
        try:
            is_audio_ = await is_audio(stream_link)
        except:
            is_audio_ = False
            LOGGER.error("Unable to get Audio properties within time.")
        if not is_audio_:
            k = await msg.edit("این لینک نامعتبره نوبه سگ.")
            await delete_messages([m, k])
            return
        try:
            dur=await get_duration(stream_link)
        except:
            dur=0
        if dur != 0:
            k = await msg.edit("این پخش زنده نیس پس باید از این دستور استفاده کنی: /play.")
            await delete_messages([m, k])
            return
        k, msg_=await stream_from_link(stream_link)
        if k == False:
            k = await msg.edit(msg_)
            await delete_messages([m, k])
            return
        if Config.msg.get('player'):
            await Config.msg['player'].delete()
        Config.msg['player']=await msg.edit(f"[استریم]({stream_link}) شروع شد. ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ", disable_web_page_preview=True, reply_markup=await get_buttons())
        await delete_messages([m])
        


admincmds=["yplay", "leave", "pause", "resume", "skip", "restart", "volume", "shuffle", "clearplaylist", "export", "import", "update", 'replay', 'logs', 'stream', 'fplay', 'schedule', 'record', 'slist', 'cancel', 'cancelall', 'vcpromote', 'vcdemote', 'refresh', 'rtitle', 'seek', 'vcmute', 'unmute',
f'stream@{Config.BOT_USERNAME}', f'logs@{Config.BOT_USERNAME}', f"replay@{Config.BOT_USERNAME}", f"yplay@{Config.BOT_USERNAME}", f"leave@{Config.BOT_USERNAME}", f"pause@{Config.BOT_USERNAME}", f"resume@{Config.BOT_USERNAME}", f"skip@{Config.BOT_USERNAME}", 
f"restart@{Config.BOT_USERNAME}", f"volume@{Config.BOT_USERNAME}", f"shuffle@{Config.BOT_USERNAME}", f"clearplaylist@{Config.BOT_USERNAME}", f"export@{Config.BOT_USERNAME}", f"import@{Config.BOT_USERNAME}", f"update@{Config.BOT_USERNAME}",
f'play@{Config.BOT_USERNAME}', f'schedule@{Config.BOT_USERNAME}', f'record@{Config.BOT_USERNAME}', f'slist@{Config.BOT_USERNAME}', f'cancel@{Config.BOT_USERNAME}', f'cancelall@{Config.BOT_USERNAME}', f'vcpromote@{Config.BOT_USERNAME}', 
f'vcdemote@{Config.BOT_USERNAME}', f'refresh@{Config.BOT_USERNAME}', f'rtitle@{Config.BOT_USERNAME}', f'seek@{Config.BOT_USERNAME}', f'mute@{Config.BOT_USERNAME}', f'vcunmute@{Config.BOT_USERNAME}'
]

allcmd = ["play", "player", f"play@{Config.BOT_USERNAME}", f"player@{Config.BOT_USERNAME}"] + admincmds

@Client.on_message(filters.command(admincmds) & ~admin_filter & chat_filter)
async def notforu(_, m: Message):
    k = await _.send_cached_media(chat_id=m.chat.id, file_id="CAADBQADEgQAAtMJyFVJOe6-VqYVzAI", caption="تو اجازشو نداری گوساله", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('⚡️بجوین', url='https://t.me/ElenLiLBoT')]]))
    await delete_messages([m, k])

@Client.on_message(filters.command(allcmd) & ~chat_filter & filters.group)
async def not_chat(_, m: Message):
    if m.from_user is not None and m.from_user.id in Config.SUDO:
        buttons = [
            [
                InlineKeyboardButton('⚡️تغییر گپ', callback_data='set_new_chat'),
            ],
            [
                InlineKeyboardButton('ن', callback_data='closesudo'),
            ]
            ]
        await m.reply("تو این گپ اجازه ندارم کاری بکنم", reply_markup=InlineKeyboardMarkup(buttons))
        await delete_messages([m])
    else:
        buttons = [
            [
                InlineKeyboardButton('خالقم', url='https://t.me/ElenLiL'),
                InlineKeyboardButton('پورتال', url='https://t.me/ElenLiLBoT'),
            ]
            ]
        await m.reply("<b>نمیتونی ع من توی گپت استفاده کنی لجن [پورتال](https://t.me/ElenLiLBoT) .</b>", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))

