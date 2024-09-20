import time

from discord.ext import commands
import requests
import asyncio
import random
import pymorphy2
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
TOKEN = getenv('BOT_TOKEN') #kek
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
                time += int(i) * 60 * 60 * 24
                send_string += f' {i} days'
            if "hours" in info:
                i = info[info.index('hours') - 1]
                time += int(i) * 60 * 60
                send_string += f' {i} hours'
            if "minutes" in info:
                i = info[info.index('minutes') - 1]
                time += int(i) * 60
                send_string += f' {i} minutes'
            await ctx.send(send_string)
            await asyncio.sleep(time)
            await ctx.send('время X пришло')
        except Exception:
            await ctx.send('таймер не удалось завести\n'
                           'Отправьте комманду в форматe \' !#set_timer in X hours X minutes\'\n'
                           'Доступные промежутки времени - "days" "hours" "minutes"')


# ------------------------------------------------------------------------------------------------------------------


class MorphThings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='inf')
    async def inf_word(self, ctx, word):
        morph = pymorphy2.MorphAnalyzer()
        word = morph.parse(word)[0]
        await ctx.send(word.normal_form)

    @commands.command(name='alive')
    async def alive_word(self, ctx, wordm):
        morph = pymorphy2.MorphAnalyzer()
        word = morph.parse(wordm)[0]
        no = ' не '
        if 'NOUN' in word.tag:
            if word.tag.animacy == 'anim':
                no = ' '
            answer = morph.parse('Живое')[0]
            rod, chislo = word.tag.gender, word.tag.number
            if chislo == 'plur':
                answer = answer.inflect({f'{chislo}'}).word.lower()
            else:
                answer = answer.inflect({f'{rod}', f'{chislo}'}).word.lower()
            await ctx.send(f'{wordm}{no}{answer}')
        else:
            await ctx.send(f'не существительное')

    @commands.command(name='numerals')
    async def numerals(self, ctx, word, num):
        morph = pymorphy2.MorphAnalyzer()
        word = morph.parse(word)[0]
        await ctx.send(f"{num} {word.make_agree_with_number(int(num)).word}")

    @commands.command(name='noun')
    async def noun_transform(self, ctx, word, p, c):
        try:
            morph = pymorphy2.MorphAnalyzer()
            word = morph.parse(word)[0]
            if c == 'plural':
                await ctx.send(word.inflect({p, 'plur'}).word)
            else:
                await ctx.send(word.inflect({p, 'sing'}).word)
        except Exception:
            await ctx.send("проверьте формат команды \'\"!#noun word noun_case number_state\"\n"
                           "или указанный вами падеж и число")

    @commands.command(name='morph')
    async def morph(self, ctx, word):
        morph = pymorphy2.MorphAnalyzer()
        answer = morph.parse(word)[0]
        await ctx.send(f'слово "{word}" имеет начальную форму - {answer.normal_form}\n'
                       f'и такие характеристики ->{answer.tag}\n'
                       f'ознакомиться с ними можно по ссылке https://pymorphy2.readthedocs.io/en/stable/user/grammemes.html#grammeme-docs')


# ------------------------------------------------------------------------------------------------------------------


class WeatherThings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.place = 'Екатеринбург'
        self.lon = 60.597474
        self.lat = 56.838011

    @commands.command(name='place')
    async def choose_place(self, ctx, place):
        try:
            search_api_server = "https://search-maps.yandex.ru/v1/"
            api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
            search_params = {
                "apikey": api_key,
                "text": place,
                "lang": "ru_RU"
            }
            response = requests.get(search_api_server, params=search_params).json()
            self.place = place
            self.lon = response['features'][0]['geometry']['coordinates'][0]
            self.lat = response['features'][0]['geometry']['coordinates'][1]
        except Exception:
            await ctx.send('Не удалось сменить место прогноза')
        await ctx.send(f'место прогноза изменено на {place}')

    @commands.command(name='current')
    async def current_weather(self, ctx):
        if self.place:
            url = "https://api.weather.yandex.ru/v2/forecast?"
            querystring = {"lat": self.lat,
                           "lon": self.lon,
                           "extra": 'false',
                           "lang": "ru_RU",
                           'hours': 'false'}
            headers = {'X-Yandex-API-Key': "ac63b6e7-9595-49e4-bd2c-6538ba356a82"}
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
            headers = {'X-Yandex-API-Key': getenv('YANDEX_TOKEN')}
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
            'x-rapidapi-key': getenv('RAPID_TOKEN'),
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
        self.YDL_OPTIONS = {'format': 'worstaudio/best',
                            'simulate': 'True', 'preferredquality': '192',
                            'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.chrome_options = Options()
        self.chrome_options.add_argument("headless")

        self.track = {}
        self.voices = {}
        self.queue = {}
        self.play_choose = {}

    @commands.command(name='connect_channel')
    async def connect_channel(self, ctx):
        global voice, channel
        channel = ctx.message.author.voice.channel
        print(ctx.guild.id)
        self.voices[ctx.guild.id] = get(self.bot.voice_clients, guild=ctx.guild)
        self.queue[ctx.guild.id] = []
        self.track[ctx.guild.id] = ''
        self.play_choose[ctx.guild.id] = {}
        if self.voices[ctx.guild.id] and self.voices[ctx.guild.id].is_connected():
            await self.voices[ctx.guild.id].move_to(channel)
        else:
            self.voices[ctx.guild.id] = await channel.connect(reconnect=True, timeout=None)

    @commands.command(name='resume_music')
    async def resume_channel_music(self, ctx):
        self.voices[ctx.guild.id].resume()

    @commands.command(name="pause_music")
    async def pause_channel_music(self, ctx):
        self.voices[ctx.guild.id].pause()

    @commands.command(name='stop_music')
    async def stop_channel_music(self, ctx):
        self.voices[ctx.guild.id].stop()

    @commands.command(name='play_radio')
    async def play_channel_radio(self, ctx):  # не работает с командой skip
        if self.voices[ctx.guild.id].is_playing():
            await ctx.send(f'{ctx.message.author.mention}, музыка уже проигрывается.')
        else:
            self.voices[ctx.guild.id].play(FFmpegPCMAudio(executable='./FFmpeg/bin/ffmpeg.exe',
                                                          source='http://icecast-studio21.cdnvideo.ru/S21cl_1p'))  # 'http://ep128.hostingradio.ru:8030/ep128'

    @commands.command(name='play')
    async def play_channel_music(self, ctx, *track, next=False):
        print('----')
        print(track[0])
        print(len(track), 'https://www.youtube.com/watch' in track[0])
        print('------')
        if len(track) == 1 and 'https://www.youtube.com/watch' in track[0]:
            track = track[0]
            if self.voices[ctx.guild.id].is_playing() and not next:
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(track, download=False)
                if 'entries' in info:
                    for i in info['entries']:
                        self.queue[ctx.guild.id].append(f'https://www.youtube.com/watch?v={i["id"]}')
                        await ctx.send(f'{len(info["entries"])} треков было добавлено в очередь')
                else:
                    self.queue[ctx.guild.id].append(track)
                    await ctx.send(f'трек "{info["title"]}"- добавлен в очередб')
            else:
                if next:
                    self.voices[ctx.guild.id].stop()
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(track, download=False)
                if 'entries' in info:
                    self.track[ctx.guild.id] = f'https://www.youtube.com/watch?v={info["entries"][0]["id"]}'
                    for i in info['entries'][1:]:
                        self.queue[ctx.guild.id].append(f'https://www.youtube.com/watch?v={i["id"]}')
                    await ctx.send(f'{info["entries"][0]["title"]} был включен\n'
                                   f'{len(info["entries"]) - 1} треков было добавлено в очередь')
                    URL = info["entries"][0]['formats'][0]['url']
                    print(URL)
                    self.voices[ctx.guild.id].play(FFmpegPCMAudio(executable="/FFmpeg/bin/ffmpeg.exe", source=URL, **self.FFMPEG_OPTIONS))
                else:
                    self.track[ctx.guild.id] = track
                    URL = info['formats'][0]['url']
                    self.voices[ctx.guild.id].play(FFmpegPCMAudio(executable="/FFmpeg/bin/ffmpeg.exe", source=URL, **self.FFMPEG_OPTIONS))
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
            out = ''
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
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[0][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(aliases=['2', 'p2'])
    async def play_track_choose2(self, ctx):
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[1][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(aliases=['3', 'p3'])
    async def play_track_choose3(self, ctx):
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[2][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(name='p4')
    async def play_track_choose4(self, ctx):
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[3][1])
        else:
            await ctx.send(f'Вам нечего выбирать')

    @commands.command(name='p5')
    async def play_track_choose5(self, ctx):
        a = self.play_choose[ctx.guild.id].get(ctx.message.author, False)
        if a:
            self.play_choose[ctx.guild.id][ctx.message.author] = []
            await self.play_channel_music(ctx, a[4][1])
        else:
            await ctx.send(f'Вам нечего выбирать')



    @commands.command(name='skip')
    async def skip_channel_music(self, ctx, wo_text=False):
        if not wo_text:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.track[ctx.guild.id], download=False)
            await ctx.send(f'трек "{info["title"]}" пропущен')
        if self.queue[ctx.guild.id]:
            await self.play_channel_music(ctx, self.queue[ctx.guild.id].pop(0), next=True)
        else:
            self.track[ctx.guild.id] = ''
            self.voices[ctx.guild.id].stop()

    @commands.command(name='queue')
    async def show_queue(self, ctx):
        if self.queue[ctx.guild.id]:
            output = []
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.track[ctx.guild.id], download=False)
            await ctx.send(f'трек "{info["title"]}" сейчас играет')
            for num, i in enumerate(self.queue[ctx.guild.id]):
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(i, download=False)
                output.append(f'{num + 1} - {info["title"]}')
            await ctx.send('\n'.join(output))
        else:
            await ctx.send('очередь пуста')

    @commands.command(name="leave_channel")
    async def leave_channel(self, ctx):
        await self.voices[ctx.guild.id].disconnect()
        self.track[ctx.guild.id] = ''
        self.queue[ctx.guild.id].clear()


# ----------------------------------------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Создатель: Иван Старцев"))


@commands.command(name='help_bot')
async def help(ctx):
    await ctx.send('Commands\n'
                   '"!#roll_dice" выбрасывает случайное число от 1 до 6\n'
                   '"!#randint x y" выбрасывает случайное число от x до y\n'
                   '"!#cat" случайная картинка с котиком\n'
                   '"!#dog" случайная картинка с собачкой\n'
                   '"!#set timer x days x hours x minutes" устанавливает таймер на выбранный промежуток времени\n'
                   '"!#numerals num word" cогласовывает слово (word) с числом (num)\n'  # +
                   '"!#alive" определяет живое ли существительное\n'  # +
                   '"!#noun word noun_case number_state" изменяет слово в соответствии с введенным падежом и числом\n'  # +
                   '"!#inf word" выводит инфинитив слова\n'  # +
                   '"!#morph word" морфологический разбор слова')


bot.add_cog(MorphThings(bot))
bot.add_cog(AllThings(bot))
bot.add_cog(WeatherThings(bot))
bot.add_cog(LanguageThings(bot))
bot.add_cog(MusicThings(bot))
bot.run(TOKEN)

