import discord
from discord.ext import commands
import yt_dlp as youtube_dl

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # váže se na ipv4, protože ipv6 adresy někdy způsobují problémy
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or discord.Client(intents=intents).loop
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # vezme první položku z playlistu
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.event
async def on_ready():
    print(f"Přihlášen jako {bot.user}")

@bot.command(name='play', help='Pro přehrání písně')
async def play(ctx, url):
    voice_channel = ctx.author.voice.channel
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel = await voice_channel.connect()
        voice_channel.play(discord.FFmpegPCMAudio(source=filename))
    await ctx.send(f'**Nyní se přehrává:** {filename}')

@bot.command(name='join', help='Připojí bota do hlasového kanálu')
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    await ctx.send(f"Připojil(a) jsem se do kanálu {voice_channel.name}")

@bot.command(name='leave', help='Přinutí bota opustit hlasový kanál')
async def leave(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel:
        await voice_channel.disconnect()
        await ctx.send("Opustil jsem hlasový kanál")
    else:
        await ctx.send("Bot není připojený k hlasovému kanálu.")

@bot.command(name='stop', help='Zastaví přehrávání písně')
async def stop(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.stop()
        await ctx.send("Přehrávání zastaveno")
    else:
        await ctx.send("Bot v současné době nic nepřehrává.")

@bot.command(name='pause', help='Pozastaví přehrávání písně')
async def pause(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.pause()
        await ctx.send("Píseň pozastavena")
    else:
        await ctx.send("Bot v současné době nic nepřehrává.")

@bot.command(name='resume', help='Obnoví přehrávání písně')
async def resume(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel.is_paused():
        voice_channel.resume()
        await ctx.send("Píseň byla obnovena")
    else:
        await ctx.send("Bot před tímto nepřehrával nic. Použijte příkaz !play")

bot.run("Místo textu sem zadej token tvého bota")
