import sqlite3

import youtube_dl.utils
from discord.ext import commands
import requests
import asyncio
import random
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from discord.utils import get
import discord
from dotenv import load_dotenv
from youtube_dl import YoutubeDL
from bs4 import BeautifulSoup
from asyncio import sleep
from os import getenv
from sys import exit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


load_dotenv()
bot = Bot(command_prefix='!#')
bot.remove_command("help")
TOKEN = getenv('BOT_TOKEN')  # подставить свой
YANDEX_TOKEN = getenv('YANDEX_TOKEN')  # подставить свой, функция с погодой работает, только у меня кончился токен
RAPID_TOKEN = getenv('RAPID_TOKEN')

if not TOKEN:
    exit('Error: no token provided')
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']
bots = {}


# ------------------------------------------------------------------


class AllThings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll_dice')
    async def roll_dice(self, ctx):
        res = [random.choice(dashes) for _ in range(int(1))]
        await ctx.send(" ".join(res))

    @commands.command(name='randint')
    async def my_randint(self, ctx, min_int, max_int):
        num = random.randint(int(min_int), int(max_int))
        await ctx.send(num)

    @commands.command(name="cat")
    async def random_cat(self, ctx):
        await ctx.send(requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url'])

    @commands.command(name="dog")
    async def random_dog(self, ctx):
        await ctx.send(requests.get('https://dog.ceo/api/breeds/image/random').json()['message'])

    @commands.command(name='set_timer')
    async def set_timer(self, ctx, *info):
        try:
            time = 0
            info = info[1:]
            send_string = 'Таймер запущен на'
            if 'days' in info:
                i = info[info.index('days') - 1]
                if i >= 0:
                    time += int(i) * 60 * 60 * 24
                    send_string += f' {i} days'
                else:
                    raise Exception
            if "hours" in info:
                i = info[info.index('hours') - 1]
                if i >= 0:
                    time += int(i) * 60 * 60
                    send_string += f' {i} hours'
                else:
                    raise Exception
            if "minutes" in info:
                i = info[info.index('minutes') - 1]
                if i >= 0:
                    time += int(i) * 60
                    send_string += f' {i} minutes'
                else:
                    raise Exception
            await ctx.send(send_string)
            await asyncio.sleep(time)
            await ctx.send('время X пришло')
        except Exception:
            await ctx.send('таймер не удалось завести\n'
                           'Отправьте комманду в форматe \' !#set_timer in X hours X minutes\'\n'
                           'Доступные промежутки времени - "days" "hours" "minutes"')


# ------------------------------------------------------------------------------------------------------------------

class WeatherThings(commands.Cog):  # У меня кончился пробный период токена, но он правда работает
    def __init__(self, bot):
        self.bot = bot
        self.place = 'Екатеринбург'
        self.lon = 60.597474
        self.lat = 56.838011

    @commands.command(name='place')
    async def choose_place(self, ctx, place):
        try:
            search_api_server = "https://search-maps.yandex.ru/v1/"
            api_key = YANDEX_TOKEN
            search_params = {
                "apikey": api_key,
                "text": place,
                "lang": "ru_RU"
            }
            response = requests.get(search_api_server, params=search_params).json()
            self.place = place
            self.lon = response['features'][0]['geometry']['coordinates'][0]
            self.lat = response['features'][0]['geometry']['coordinates'][1]
            await ctx.send(f'место прогноза изменено на {place}')
        except Exception:
            await ctx.send('Не удалось сменить место прогноза')

    @commands.command(name='current')
    async def current_weather(self, ctx):
        if self.place:
            url = "https://api.weather.yandex.ru/v2/forecast?"
            querystring = {"lat": self.lat,
                           "lon": self.lon,
                           "extra": 'false',
                           "lang": "ru_RU",
                           'hours': 'false'}
            headers = {'X-Yandex-API-Key': YANDEX_TOKEN}
            response = requests.request("GET", url, headers=headers, params=querystring).json()
            await ctx.send(f'Погода в {self.place} на {response["forecasts"][0]["date"]}\n'
                           f'Температура - {response["fact"]["temp"]}\n'
                           f'Давление - {response["fact"]["pressure_mm"]}\n'
                           f'Влажность - {response["fact"]["humidity"]}\n'
                           f'Погодноe описаниe - {response["fact"]["condition"]}\n'
                           f'Направление ветра - {response["fact"]["wind_dir"]}\n'
                           f'Сила ветра - {response["fact"]["wind_speed"]}\n')
        else:
            await ctx.send('выберите место прогноза через команду "!#place"')

    @commands.command(name='forecast')
    async def take_forecast(self, ctx, days):
        if self.place:
            url = "https://api.weather.yandex.ru/v2/forecast?"
            querystring = {"lat": self.lat,
                           "lon": self.lon,
                           "extra": 'false',
                           "lang": "ru_RU",
                           'hours': 'false',
                           'limit': days}
            headers = {'X-Yandex-API-Key': YANDEX_TOKEN}
            response = requests.request("GET", url, headers=headers, params=querystring).json()
            for i in response["forecasts"]:
                await ctx.send(f'----------------------------------------\n'
                               f'Погода в {self.place} на {i["date"]}\n'
                               f'Температура - {i["parts"]["day"]["temp_avg"]}\n'
                               f'Давление - {i["parts"]["day"]["pressure_mm"]}\n'
                               f'Влажность - {i["parts"]["day"]["humidity"]}\n'
                               f'Погодноe описаниe - {i["parts"]["day"]["condition"]}\n'
                               f'Направление ветра - {i["parts"]["day"]["wind_dir"]}\n'
                               f'Сила ветра - {i["parts"]["day"]["wind_speed"]}\n'
                               f'----------------------------------------\n')
        else:
            await ctx.send('выберите место прогноза через команду "!#place"')


# ------------------------------------------------------------------------------------------------------------------

class LanguageThings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lang = 'en|ru'

    @commands.command(name='help_lang')
    async def help_lang(self, ctx):
        await ctx.send(f"напишите '!#text' и текст для перевода, чтобы перевести\n"
                       f"напишите '!#set_lang' и язык с которого идет перевод-язык на который переводиться")

    @commands.command(name='set_lang')
    async def change_translate_lang(self, ctx, lang):
        self.lang = '|'.join(lang.split('-'))
        await ctx.send(f'установлен язык - {self.lang}')

    @commands.command(name='text')
    async def translate_text(self, ctx, *text):
        url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
        querystring = {"langpair": self.lang, "q": ' '.join(text), "mt": "1", "onlyprivate": "0"}
        headers = {
            'x-rapidapi-key': RAPID_TOKEN,
            'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        print(response)
        await ctx.send(response['responseData']['translatedText'])


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class MusicThings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.YDL_OPTIONS = {'format': 'bestaudio/best',
                            'simulate': 'True', 'preferredquality': '192',
                            'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.chrome_options = Options()
        self.chrome_options.add_argument("headless")

        self.started = {}
        self.track = {}
        self.voices = {}
        self.queue = {}
        self.redacting = {}
        self.play_choose = {}

        self.con = sqlite3.connect("discorddatabase.sqlite")

    @commands.command(name='connect_channel')
    async def connect_channel(self, ctx):
        try:
            global voice, channel
            if not self.started.get(ctx.guild.id):
                await self.start(ctx)
            channel = ctx.message.author.voice.channel
            self.voices[ctx.guild.id] = get(self.bot.voice_clients, guild=ctx.guild)
            if self.voices[ctx.guild.id] and self.voices[ctx.guild.id].is_connected():
                await self.voices[ctx.guild.id].move_to(channel)
                return True
            else:
                self.voices[ctx.guild.id] = await channel.connect(reconnect=True, timeout=None)
                return True
        except Exception:
            await ctx.send('Чтобы включить треки, необходимо находиться в каком-то голосовом канале')
            return False

    @commands.command(name='start')
    async def start(self, ctx):
        if self.started.get(ctx.guild.id):
            await ctx.send('Я уже запущен ;)')
        self.started[ctx.guild.id] = True
        self.queue[ctx.guild.id] = []
        self.track[ctx.guild.id] = [] # изменить на список с ссылкой и названием, быстрее в 10 раз
        self.play_choose[ctx.guild.id] = {}
        self.redacting[ctx.guild.id] = {}

    @commands.command(name='resume_music')
    async def resume_channel_music(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        self.voices[ctx.guild.id].resume()

    @commands.command(name="pause_music")
    async def pause_channel_music(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        self.voices[ctx.guild.id].pause()

    @commands.command(name='stop_music')
    async def stop_channel_music(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        self.voices[ctx.guild.id].stop()

    @commands.command(name='play')
    async def play_channel_music(self, ctx, *track, next=False, hide=False):
        try:
            a = self.voices[ctx.guild.id].is_connected()
            if not a:
                await self.connect_channel(ctx)
        except Exception:
            await self.connect_channel(ctx)
        """print('----')
        print(track[0])
        print(len(track), 'https://www.youtube.com/watch' in track[0])
        print('------')
        print(track)"""
        if len(track) == 1 and 'https://www.youtube.com/watch' in track[0]:
            track = track[0]
            print(self.voices[ctx.guild.id].is_playing())
            if self.voices[ctx.guild.id].is_playing() and not next:
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(track, download=False)
                if 'entries' in info:
                    for i in info['entries']:
                        self.queue[ctx.guild.id].append([f'https://www.youtube.com/watch?v={i["id"]}', i["title"]])
                        await ctx.send(f'{len(info["entries"])} треков было добавлено в очередь')
                else:
                    self.queue[ctx.guild.id].append([track, info["title"]])
                    if not hide:
                        await ctx.send(f'трек "{info["title"]}"- добавлен в очередь')
            else:
                if next:
                    self.voices[ctx.guild.id].stop()
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(track, download=False)
                if 'entries' in info:
                    self.track[ctx.guild.id] = [f'https://www.youtube.com/watch?v={info["entries"][0]["id"]}',
                                                info["entries"][0]["title"]]
                    for i in info['entries'][1:]:
                        self.queue[ctx.guild.id].append([f'https://www.youtube.com/watch?v={i["id"]}', i["title"]])
                    await ctx.send(f'{info["entries"][0]["title"]} был включен\n'
                                   f'{len(info["entries"]) - 1} треков было добавлено в очередь')
                    URL = info["entries"][0]['formats'][0]['url']
                    self.voices[ctx.guild.id].play(FFmpegPCMAudio(executable="/FFmpeg/bin/ffmpeg.exe",
                                                                  source=URL, **self.FFMPEG_OPTIONS))
                else:
                    self.track[ctx.guild.id] = [track, info["title"]]
                    URL = info['formats'][0]['url']
                    self.voices[ctx.guild.id].play(FFmpegPCMAudio(executable="/FFmpeg/bin/ffmpeg.exe",
                                                                  source=URL, **self.FFMPEG_OPTIONS))
                while self.voices[ctx.guild.id].is_playing():
                    await sleep(1)
                if not self.voices[ctx.guild.id].is_paused():
                    await self.skip_channel_music(ctx, wo_text=True)
        else:
            URL = f"https://www.youtube.com/results?search_query={'+'.join(track)}"
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(URL)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            videos = soup.find_all("ytd-video-renderer", {"class": "style-scope ytd-item-section-renderer"})
            out = 'Выберите трек командой "!#p<1-5>"'
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            for i, video in enumerate(videos[:5]):
                a = video.find("a", {"id": "thumbnail"})
                text = video.find("yt-formatted-string", {"class": "style-scope ytd-video-renderer"})
                name = text.get_text()
                link = "https://www.youtube.com" + a.get("href")
                self.play_choose[ctx.guild.id][ctx.message.author].append([name, link])
                out += f'{i + 1} ---- {name}\n'
            await ctx.send(out)

    @commands.command(aliases=['1', 'p1'])
    async def play_track_choose1(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[0][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(aliases=['2', 'p2'])
    async def play_track_choose2(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[1][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(aliases=['3', 'p3'])
    async def play_track_choose3(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[2][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(aliases=['4', 'p4'])
    async def play_track_choose4(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[3][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(aliases=['5', 'p5'])
    async def play_track_choose5(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[4][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(name='skip')
    async def skip_channel_music(self, ctx, *num, wo_text=False):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        if num:
            try:
                if int(num[0]) == float(num[0]) and int(num[0]) > 0:
                    num = int(num[0])
                    self.queue[ctx.guild.id] = self.queue[ctx.guild.id][num - 1:]
                    if self.queue[ctx.guild.id]:
                        await self.play_channel_music(ctx, self.queue[ctx.guild.id].pop(0)[0], next=True)
                    else:
                        self.track[ctx.guild.id] = []
                        self.voices[ctx.guild.id].stop()
            except Exception:
                await ctx.reply('Число скипов в неправильном формате.')
        else:
            if not wo_text:
                await ctx.send(f'трек "{self.track[ctx.guild.id][1]}" пропущен')
            if self.queue[ctx.guild.id]:
                await self.play_channel_music(ctx, self.queue[ctx.guild.id].pop(0)[0], next=True)
            else:
                self.track[ctx.guild.id] = []
                self.voices[ctx.guild.id].stop()

    @commands.command(name='clearqueue')
    async def clear_queue(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        self.queue[ctx.guild.id].clear()

    @commands.command(name='clearall')
    async def clear_all(self, ctx, hide=False):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        self.queue[ctx.guild.id] = []
        self.track[ctx.guild.id] = []
        self.voices[ctx.guild.id].stop()
        if hide:
            await ctx.send('Очередь была удалена, запущен выбранный плейлист')
        else:
            await ctx.send('Очередь была удалена, текущий трек выключен')

    @commands.command(name='queue')
    async def show_queue(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        if self.queue[ctx.guild.id]:
            output = []
            await ctx.send(f'трек "{self.track[ctx.guild.id][1]}" сейчас играет')
            for num, i in enumerate(self.queue[ctx.guild.id]):
                output.append(f'{num + 1} - {i[1]}')
            await ctx.send('\n'.join(output))
        else:
            if self.track[ctx.guild.id]:
                await ctx.send(f'очередь пуста, сейчас играет - {self.track[ctx.guild.id][1]}')
            else:
                await ctx.send('очередь пуста')

    @commands.command(name="leave_channel")
    async def leave_channel(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        await self.voices[ctx.guild.id].disconnect()
        self.track[ctx.guild.id] = []
        self.queue[ctx.guild.id].clear()

    @commands.command(name='createpl')
    async def create_playlist(self, ctx, *name):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        if not self.redacting[ctx.guild.id].get(ctx.message.author, False):
            cur = self.con.cursor()
            serverid = await self.get_serverid(ctx)
            namelock = await self.checkname(serverid, " ".join(name))
            if not namelock:
                cur.execute('''INSERT into discordplaylists(idserver, name, author) VALUES(?, ?, ?)''',
                            (serverid, ' '.join(name), ctx.message.author.id))
                self.con.commit()
                await ctx.reply(f'Вы создали плейлист с названием {" ".join(name)}\n'
                                f'Сейчас вы в режиме редактирования плейлиста\n'
                                f'чтобы выйти из него отправьте "stopredactpl"')
                await self.redact_playlist(ctx, ' '.join(name))
            else:
                await ctx.reply('Плейлист с таким названием уже есть на вашем сервере\n'
                                'Придумайте другое имя или попросите создателя его изменить')
        else:
            await ctx.reply(f'Чтобы создать новый плейлист, необходимо выйти из режима редактирования\n'
                            f'отправьте команду "stopredactpl"')

    @commands.command(name='redactpl')  # писать функции редактирования и имя плейлиста
    async def redact_playlist(self, ctx, *name):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        serverid = await self.get_serverid(ctx)
        playlistname = await self.checkname(serverid, " ".join(name), author=ctx.message.author.id)
        if playlistname:
            self.redacting[ctx.guild.id][ctx.message.author] = [' '.join(name), 0]  # 0 редактирование 1 удаление
            await ctx.send(f'Чтобы получить помощь по редактированию, отправьте команду "!#help redact"')
        else:
            await ctx.reply(f'Плейлиста "{" ".join(name)}" нету на сервере или он принадлежит не вам \n'
                            f'чтобы узнать какие плейлисты вы можете отредактировать отправьте команду "showpl my"')

    @commands.command(name='redactnamepl')
    async def change_playlist_name(self, ctx, *name):  # не забыть сменить имя в self.redacting +
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.redacting[ctx.guild.id].get(ctx.message.author, False)
        serverid = await self.get_serverid(ctx)
        namelock = await self.checkname(serverid, ' '.join(name))
        if a and not namelock:
            cur = self.con.cursor()
            cur.execute('''UPDATE discordplaylists SET name = ? WHERE name like ? and idserver like ?''',
                        (' '.join(name), a[0], serverid))
            self.redacting[ctx.guild.id][ctx.message.author] = [' '.join(name), 0]
            self.con.commit()
            await ctx.reply(f'Вы успешно сменили название плейлиста с {a[0]} на {" ".join(name)}')
        elif a and namelock:
            await ctx.reply(f'Вы пытались сменить имя на уже существующее, попробуйте другое.')
        else:
            await ctx.reply(f'Чтобы сменить имя плейлиста, нужно находиться в режиме редактирования\n'
                            f'Для этого отправьте команду "redactpl <playlistname>"')

    @commands.command(name='stopredactpl')
    async def stop_redack_playlist(self, ctx):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        if self.redacting[ctx.guild.id].get(ctx.message.author, False):
            self.redacting[ctx.guild.id][ctx.message.author] = False
            await ctx.send('Вы вышли из режима редактирования')
        else:
            await ctx.send('Вы не в режиме редактирования ;)')

    @commands.command(name='addtrack')
    async def add_track_in_playlist(self, ctx, *track):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.redacting[ctx.guild.id].get(ctx.message.author, False)
        if a:
            if len(track) == 1 and 'https://www.youtube.com/watch' in track[0]:
                track = track[0]
                try:
                    with YoutubeDL(self.YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(track, False)
                    if 'entries' in info:
                        await ctx.send('Увы, но плейлисты я не принимаю(')
                    else: # тут жара самая
                        cur = self.con.cursor()
                        serverid = await self.get_serverid(ctx)
                        playlistid = cur.execute("""SELECT id from discordplaylists where name like ? and idserver like ?""", (a[0], serverid)).fetchall()[0][0]
                        cur.execute("""INSERT into playlisttracks(id, trackname, url) VALUES(?, ?, ?)""", (playlistid, info["title"], track))
                        self.con.commit()
                        await ctx.send(f'трек "{info["title"]}"- добавлен в плейлист')
                except youtube_dl.utils.DownloadError:
                    await ctx.send('Видео с такой ссылкой нет')
            else:
                await ctx.send('Это не ссылка на youtube')
        else:
            await ctx.send('Вы не в режиме редактирования ;)')

    @commands.command(name="deletepl")
    async def delete_playlist(self, ctx, *answer):
        if not self.started.get(ctx.guild.id):
            await self.start(ctx)
        a = self.redacting[ctx.guild.id].get(ctx.message.author, False)
        if a:
            if a[1] != 1:
                await ctx.reply(f'Необходимо подтверждение\n'
                                f'Чтобы удалить плейлист {a[0]} отправьте команду "deletepl YES"\n'
                                f'Иначе отправьте "deletepl"')
                self.redacting[ctx.guild.id][ctx.message.author] = [a[0], 1]
            elif a[1] == 1 and answer[0] == 'YES':
                cur = self.con.cursor()
                severid = await self.get_serverid(ctx)
                playlistid = cur.execute("""SELECT id from discordplaylists 
                where idserver like ? and name like ? and author like ?""",
                                         (severid, a[0], ctx.message.author.id)).fetchall()[0][0]
                cur.execute("""DELETE from discordplaylists where id like ?""", (playlistid, ))
                cur.execute("""DELETE from playlisttracks where id like ?""", (playlistid, ))
                self.con.commit()
                await ctx.reply(f'Плейлист с названием {a[0]} был успешно удалён!')
                await self.stop_redack_playlist(ctx)

            else:
                self.redacting[ctx.guild.id][ctx.message.author] = [a[0], 0]
                await ctx.reply(f'Вы вышли из режима удаления плейлиста')
        else:
            await ctx.reply('Чтобы удалить плейлист, сначала надо войти в режим редактирования\n'
                            'командой "redactpl <имя плейлиста>"')

    @commands.command(name='showpl')
    async def show_playlists(self, ctx, *mode):  # mode может быть названием плейлиста Сделать кол-во треков в плейлисте
        cur = self.con.cursor()
        serverid = await self.get_serverid(ctx)
        if mode[0] == 'my':
            playlists = cur.execute("""SELECT id, name from discordplaylists where idserver like ? and author like ?""",
                                    (serverid, ctx.message.author.id)).fetchall()
            if not playlists:
                await ctx.reply('У вас нет плейлистов на данном сервере\n'
                                'Создайте его с помощью команды "createpl <name>"')
            else:
                await self.send_answer_playlist(ctx, playlists, 'm')

        elif mode[0] in ['world', 'w']:
            playlists = cur.execute("""SELECT id, name, likes from world""").fetchall()
            if not playlists:
                await ctx.reply('Пока что в интернете нет плейлистов\n'
                                'Создайте его с помощью команды "createpl <name>" \n'
                                'И загрузите с помощью команды "uploadplaylist <name>"')
            else:
                playlists = sorted(playlists, key=lambda x: - x[2])[:25]
                await self.send_answer_playlist(ctx, playlists, 'w')

        elif mode[0] == 'server':
            playlists = cur.execute("""SELECT id, name from discordplaylists where idserver like ?""",
                                    (serverid, )).fetchall()
            if not playlists:
                await ctx.reply('На данном сервере нету плейлистов\n'
                                'Создайте его с помощью команды "createpl <name>"')
            else:
                await self.send_answer_playlist(ctx, playlists, 's')
        else:
            await ctx.reply(f'чтобы увидеть свои плейлисты, отправьте "showpl my"\n'
                            f'чтобы увидеть плейлисты сервера, отправьте "showpl server"\n'
                            f'чтобы увидеть топ-25 плейлистов мира, отправьте "showpl world(или w)"'
                            f'Весь список плейлистов можно посмотреть на сайте')

    @commands.command(name='showpltracks')
    async def show_playlist_tracks(self, ctx, *name, world=False):
        serverid = await self.get_serverid(ctx)
        if world:
            namelock = await self.checkname(serverid, ' '.join(name), world=True)
        else:
            namelock = await self.checkname(serverid, ' '.join(name))
        if namelock:
            cur = self.con.cursor()
            reply = [f'Треки в плейлисте {" ".join(name)}:']
            if world:
                tracks = cur.execute("""SELECT trackname from worldtracks where id in 
                (select id from world where name like ?)""", (' '.join(name), )).fetchall()
            else:
                tracks = cur.execute("""SELECT trackname from playlisttracks where id in 
                (select id from discordplaylists where name like ?)""", (' '.join(name), )).fetchall()
            for i in enumerate(tracks):
                reply.append(f'{i[0] + 1} - {i[1][0]}')
            await ctx.send('\n'.join(reply))

        else:
            if world:
                await ctx.send('Плейлиста с таким названием в общем доступе')
            else:
                await ctx.send('Плейлиста с таким названием нет на сервере')

    @commands.command(name='showwpltracks')
    async def show_world_playlist_tracks(self, ctx, *name):
        await self.show_playlist_tracks(ctx, *name, world=True)

    async def send_answer_playlist(self, ctx, playlists, mode):
        cur = self.con.cursor()
        reply = []
        if mode == 'w':
            for i in playlists:
                likes = cur.execute("""SELECT likes from world where id like ?""", (i[0], )).fetchall()[0][0]
                tracks = len(cur.execute("""SELECT trackname from worldtracks where id like ?""", (i[0],)).fetchall())
                reply.append(f'{i[1]} - кол-во треков: {tracks}, кол-во лайков: {likes}')
        else:
            for i in playlists:
                tracks = len(cur.execute("""SELECT trackname from playlisttracks where id like ?""", (i[0],)).fetchall())
                reply.append(f'{i[1]} - кол-во треков: {tracks} ')
        a = '\n'.join(reply)
        if mode == 'm':
            await ctx.reply(f'{ctx.message.author.name}, ваш список плейлистов:\n{a}')
        elif mode == 's':
            await ctx.reply(f'Cписок плейлистов сервера:\n{a}')
        elif mode == 'w':
            await ctx.reply(f'Топ-25 плейлистов:\n{a}')

    @commands.command(name='ppl')
    async def play_playlist(self, ctx, *name, clear=False, world=False):
        try:
            a = self.voices[ctx.guild.id].is_connected()
            if not a:
                connect = await self.connect_channel(ctx)
            else:
                connect = True
        except Exception:
            connect = await self.connect_channel(ctx)
        if connect:
            serverid = await self.get_serverid(ctx)
            if world:
                namelock = await self.checkname(serverid, ' '.join(name), world=True)
            else:
                namelock = await self.checkname(serverid, ' '.join(name))
            if namelock:
                cur = self.con.cursor()
                if world:
                    tracksurl = cur.execute("""SELECT url, trackname from worldtracks where id in
                    (select id from world where name like ?)""", (' '.join(name), )).fetchall()
                else:
                    tracksurl = cur.execute("""SELECT url, trackname from playlisttracks where id in 
                    (select id from discordplaylists where name like ? and idserver like ?)""",
                                            (' '.join(name), serverid)).fetchall()
                if tracksurl:
                    if clear:
                        await self.clear_all(ctx, hide=True)
                    for i in tracksurl:
                        self.queue[ctx.guild.id].append([i[0], i[1]])
                    if not self.voices[ctx.guild.id].is_playing():
                        await ctx.send(f'плейлист был успешно запущен')
                        await self.play_channel_music(ctx, self.queue[ctx.guild.id].pop(0)[0], hide=True)
                    else:
                        await ctx.send(f'треки из плейлиста были добавлены в очередь')
                else:
                    await ctx.send(f'В выбранном плейлисте нету треков')
            else:
                await ctx.send('Плейлиста с таким именем не существует')

    @commands.command(name='pplclear')
    async def play_playlist_clear(self, ctx, *name):
        await self.play_playlist(ctx, *name, clear=True)

    @commands.command(name='pwpl')  # предложить поставить лайк
    async def play_world_playlist(self, ctx, *name):
        await self.play_playlist(ctx, *name, world=True)

    @commands.command(name='pwplclear')
    async def play_world_playlist_clear(self, ctx, *name):
        await self.play_playlist(ctx, *name, clear=True, world=True)

    @commands.command(name='uploadplaylist')
    async def upload_a_playlist(self, ctx, *name):
        serverid = await self.get_serverid(ctx)
        playlistname = await self.checkname(serverid, " ".join(name), author=ctx.message.author.id)
        playlistnameworld = await self.checkname(serverid, " ".join(name), world=True)
        if playlistname and not playlistnameworld:
            cur = self.con.cursor()
            cur.execute("""INSERT into world(name, likes) VALUES(?, ?)""", (' '.join(name), 0))
            self.con.commit()
            playlistid = cur.execute("""SELECT id from world where name like ?""", (' '.join(name), )).fetchall()[0][0]
            tracks = cur.execute("""SELECT trackname, url from playlisttracks where id in 
            (select id from discordplaylists where name like ?)""", (' '.join(name), )).fetchall()
            for i in tracks:
                cur.execute("""INSERT into worldtracks(id, trackname, url) VALUES(?, ?, ?)""", (playlistid, i[0], i[1]))
            self.con.commit()
            await ctx.send(f'Вы успешно выложили плейлист {" ".join(name)} в интернет')
        elif playlistname and playlistnameworld:
            await ctx.reply(f'Плейлист с таким названием уже существует, вам необходимо придумать другое\n'
                            f'Для этого войдите в режим редактирования и смените его название "redactpl'
                            f' {" ".join(name)}"')
        else:
            await ctx.reply(f'Плейлиста "{" ".join(name)}" нету на сервере или он принадлежит не вам \n'
                            f'чтобы узнать какие плейлисты вы можете загрузить отправьте команду "showpl my"')

    @commands.command(name='like')
    async def like_world_playlist(self, ctx, *name):
        serverid = await self.get_serverid(ctx)
        playlistnameworld = await self.checkname(serverid, " ".join(name), world=True)
        if playlistnameworld:
            cur = self.con.cursor()
            playlistid = cur.execute("""SELECT id from world where name like ?""", (' '.join(name),)).fetchall()[0][0]
            checkuser = cur.execute("""SELECT user from discordlikes where user like ? and id like ?""",
                                    (ctx.message.author.id, playlistid)).fetchall()
            if not checkuser:
                likes = cur.execute("""SELECT likes from world where name like ?""", (' '.join(name),)).fetchall()[0][0]
                cur.execute("""UPDATE world SET likes = ? where name like ?""", (likes + 1, ' '.join(name)))
                cur.execute("""INSERT into discordlikes(id, user) VALUES(?, ?)""", (playlistid, ctx.message.author.id))
                self.con.commit()
                await ctx.send('Лайк поставлен! <3')
            else:
                await ctx.send('Вы уже поставили лайк на данный плейлист)')
        else:
            await ctx.send('Плейлиста с таким названием нету или, '
                           'возможно, вы хотели поставить лайк на плейлист сервера, но так я не умею')

    async def get_serverid(self, ctx): # +
        cur = self.con.cursor()
        id = cur.execute("SELECT id from discordservers WHERE serverid like ?", (ctx.guild.id, )).fetchall()
        if not id:
            cur.execute('''INSERT into discordservers(serverid) VALUES(?)''', (ctx.guild.id, ))
        self.con.commit()
        id = cur.execute("SELECT id from discordservers WHERE serverid like ?", (ctx.guild.id, )).fetchall()
        return id[0][0]

    async def checkname(self, id, name, author=False, world=False): # +
        cur = self.con.cursor()
        if author:
            name = cur.execute("""SELECT name from discordplaylists WHERE idserver like ? and name like ? and
             author like ?""",
                               (id, name, author)).fetchall()
        elif world:
            name = cur.execute("""SELECT name from world WHERE name like ?""", (name, )).fetchall()
        else:
            name = cur.execute("""SELECT name from discordplaylists WHERE idserver like ? and name like ?""",
                               (id, name)).fetchall()
        if name:
            return True
        else:
            return False

# ----------------------------------------------------------------------------------------------------------------------


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("!#help для получения информации"))


@bot.command(name='help')
async def send_help(ctx, *name):
    if not name:
        emb = discord.Embed(title='Основные команды', color=discord.Color.blue())
        emb.add_field(name='--------USELESS--------', value='** **', inline=False)
        emb.add_field(name='!#roll_dice', value='выбрасывает случайное число от 1 до 6', inline=False)
        emb.add_field(name='!#randint x y', value='выбрасывает случайное число от x до y', inline=False)
        emb.add_field(name='!#cat', value='случайная картинка с котиком', inline=False)
        emb.add_field(name='!#dog', value='случайная картинка с собачкой', inline=False)
        emb.add_field(name='!#set_timer in ? days ? hours ? minutes', value='запускает таймер на выбранное'
                                                                            ' кол-во времени', inline=False)

        emb.add_field(name='--------Команды связанные с погодой--------', value='** **', inline=False)
        emb.add_field(name='!#place <text>', value='Выбор места для получения информации и погоде по'
                                                   ' умолчанию Екатеринбург', inline=False)
        emb.add_field(name='!#current', value='показывает текущую погоду в выбранном месте', inline=False)
        emb.add_field(name='!#forecast x', value='Показывает прогноз погоды на x дней вперёд', inline=False)

        emb.add_field(name='--------Команды связанные с переводчиком--------', value='** **', inline=False)
        emb.add_field(name='!#set_lang <язык с которого переводиться>-<язык на который переводиться>',
                      value='Устанавливает язык для переводчика', inline=False)
        emb.add_field(name='!#text <текст для перевода>', value='переводит написанный в формате выбранных языков',
                      inline=False)
        emb.add_field(name='--------Команды связанные с Музыкальным ботом--------', value='** **', inline=False)

        emb.add_field(name='!#help music', value='для получения всей информации о музыкальных командах', inline=False)
        await ctx.send(embed=emb)
    elif name[0] == 'music':
        emb = discord.Embed(title='Команды связанные с музыкой:', color=discord.Color.dark_purple())
        emb.add_field(name='!#play <ссылка на видео или текст для поиска>',
                      value='если отправить ссылку, то трек сразу включиться или добавиться в очередь, если отправлен'
                            ' текст,\n то бот предложит 5 видео на выбор, выбрать можно командой "!#p<1-5>"'
                            ' или "!#<1-5>', inline=False)
        emb.add_field(name='!#skip <кол-во>', value='пропускает выбранное кол-во треков, если количество не указано,'
                                                    ' бот выключает текущий трек и включает следующий', inline=False)
        emb.add_field(name='!#clearqueue', value='полностью удаляет очередь треков', inline=False)
        emb.add_field(name='!#clearall', value='удаляет очередь треков и выключает текущий', inline=False)

        emb.add_field(name='--------Плейлисты--------', value='** **', inline=False)
        emb.add_field(name='!#createpl <name>', value='на сервере создается плейлист с выбранным названием и включается'
                                                      ' режим редактирования', inline=False)
        emb.add_field(name='!#redactpl <name>', value='человек переходит в режим редактирования выбранного плейлиста,'
                                                      ' если он принадлежит ему', inline=False)
        emb.add_field(name='!#addtrack <url>', value='добавляет в плейлист трек с ссылки(работает только в режиме'
                                                     ' редактирования)', inline=False)
        emb.add_field(name='!#redactnamepl <name>', value='человек переходит в режим редактирования выбранного'
                                                          ' плейлиста, если он принадлежит ему', inline=False)
        emb.add_field(name='!#deletepl', value='удаляет плейлист(работает только в режиме редактирования)',
                      inline=False)
        emb.add_field(name='!#stopredactpl', value='человек выходит из режима редактирования(работает только в'
                                                   ' режиме редактирования)', inline=False)
        emb.add_field(name='!#showpl my', value='показывает ваши плейлисты на сервере в котором вы сейчас находитесь',
                      inline=False)
        emb.add_field(name='!#showpl server', value='показывает все плейлисты на сервере', inline=False)
        emb.add_field(name='!#showpl w(или world)', value='показывает топ-25 плейлистов выгруженных в общийдоступ',
                      inline=False)
        emb.add_field(name='!#ppl <name>', value='добавляет треки плейлиста в очередь(только плейлисты сервера)',
                      inline=False)
        emb.add_field(name='!#pplclear <name>',
                      value='удаляет очередь и сразу включаются треки плейлиста(только плейлисты сервера)',
                      inline=False)
        emb.add_field(name='!#pwpl <name>',
                      value='добавляет треки плейлиста в очередь(только плейлисты общего доступа)',
                      inline=False)
        emb.add_field(name='!#pwplclear <name>',
                      value='удаляет очередь и сразу включаются треки плейлиста(только плейлисты общего доступа)',
                      inline=False)
        emb.add_field(name='!#uploadplaylist <name>', value='загружает ВАШ плейлист в общий доступ', inline=False)
        emb.add_field(name='!#like <name>', value='поставить лайк плейлисту из общего доступа', inline=False)
        await ctx.send(embed=emb)
    elif name[0] == "redact":
        emb = discord.Embed(title='Команды связанные с редактированием', color=discord.Color.purple())
        emb.add_field(name='!#createpl <name>',
                      value='на сервере создается плейлист с выбранным названием и включается режим редактирования',
                      inline=False)
        emb.add_field(name='!#redactpl <name>',
                      value='человек переходит в режим редактирования выбранного плейлиста, если он принадлежит ему',
                      inline=False)
        emb.add_field(name='!#addtrack <url>',
                      value='добавляет в плейлист трек с ссылки(работает только в режиме редактирования)', inline=False)
        emb.add_field(name='!#redactnamepl <name>',
                      value='человек переходит в режим редактирования выбранного плейлиста, если он принадлежит ему',
                      inline=False)
        emb.add_field(name='!#deletepl', value='удаляет плейлист(работает только в режиме редактирования)',
                      inline=False)
        emb.add_field(name='!#stopredactpl',
                      value='человек выходит из режима редактирования(работает только в режиме редактирования)',
                      inline=False)
        emb.add_field(name='!#showpl my', value='показывает ваши плейлисты на сервере в котором вы сейчас находитесь',
                      inline=False)
        await ctx.send(embed=emb)


"""@bot.event
async def on_message(message):

    await bot.process_commands(message)"""  # проверка что это сообщения на сервере, а не в лс

bot.add_cog(AllThings(bot))
bot.add_cog(WeatherThings(bot))
bot.add_cog(LanguageThings(bot))
bot.add_cog(MusicThings(bot))

bot.run(TOKEN)
