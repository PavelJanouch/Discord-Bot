import discord
from discord.ext import commands
import yt_dlp as youtube_dl

intents = discord.Intents.all()                                                # Vytvoří objekt Intent, který zahrnuje všechny události
bot = commands.Bot(command_prefix='!', intents=intents)                        # Vytvoří instanci bota s prefixem '!' a předanými Intents

ytdl_format_options = {
    'format': 'bestaudio/best',                                                # Formát stahovaného zvuku (nejlepší audio)
    'restrictfilenames': True,                                                 # Omezí názvy souborů na ASCII znaky
    'noplaylist': True,                                                        # Zakáže stahování celých playlistů
    'nocheckcertificate': True,                                                # Neověřuje platnost certifikátu při stahování
    'ignoreerrors': False,                                                     # Neignoruje chyby při stahování
    'logtostderr': False,                                                      # Nevypisuje logy do stderr
    'quiet': True,                                                             # Potlačuje výstupní zprávy
    'no_warnings': True,                                                       # Potlačuje varování
    'default_search': 'auto',                                                  # Adresa zdroje na poslech (0.0.0.0 váže na všechny síťové rozhraní)                          
    'source_address': '0.0.0.0'                                                # Adresa zdroje na poslech (0.0.0.0 váže na všechny síťové rozhraní)
} 

ffmpeg_options = {
    'options': '-vn'                                                            # Nastavuje FFmpeg, aby nevysílal video, pouze zvuk
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)                                # Vytvoří instanci YoutubeDL pro manipulaci s YouTube-DL

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')                                           # Získá název písně
        self.url = data.get('url')                                               # Získá URL adresu písně

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or discord.Client(intents=intents).loop
                                                                                 # Extrahuje informace o videu z YouTube pomocí YouTube-DL
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
                                                                                 # Pokud je to playlist, vezme první položku
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename                                                          # Vrátí název souboru

@bot.event
async def on_ready():  
    print(f"Přihlášen jako {bot.user}")                                          # Vypíše zprávu, když je bot připraven

@bot.command(name='play', help='Pro přehrání písně')
async def play(ctx, url): 
    voice_channel = ctx.author.voice.channel                                     # Získá hlasový kanál, ve kterém je autor zprávy
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=bot.loop)                 # Získá název souboru ze zadané URL adresy
        voice_channel = await voice_channel.connect()                            # Připojí se k hlasovému kanálu
        voice_channel.play(discord.FFmpegPCMAudio(source=filename))              # Přehraje zvukový soubor
    await ctx.send(f'**Nyní se přehrává:** {filename}')                          # Odešle zprávu s názvem přehrávané písně

@bot.command(name='join', help='Připojí bota do hlasového kanálu')
async def join(ctx):  
    voice_channel = ctx.author.voice.channel                                     # Získá hlasový kanál, ve kterém je autor zprávy
    await voice_channel.connect()                                                # Připojí se k hlasovému kanálu
    await ctx.send(f"Připojil(a) jsem se do kanálu {voice_channel.name}")        # Odešle zprávu s potvrzením připojení

@bot.command(name='leave', help='Přinutí bota opustit hlasový kanál')
async def leave(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel:
        await voice_channel.disconnect()                                         # Odpojí bota od hlasového kanálu
        await ctx.send("Opustil jsem hlasový kanál")                             # Odešle zprávu s potvrzením opuštění hlasového kanálu
    else:  
        await ctx.send("Bot není připojený k hlasovému kanálu.")                 # Odešle zprávu, pokud bot není připojen k hlasovému kanálu

@bot.command(name='stop', help='Zastaví přehrávání písně')
async def stop(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.stop()                                                     # Zastaví přehrávání písně
        await ctx.send("Přehrávání zastaveno")                                   # Odešle zprávu s potvrzením zastavení přehrávání
    else:
        await ctx.send("Bot v současné době nic nepřehrává.")                    # Odešle zprávu, pokud bot v současné době nic nepřehrává

@bot.command(name='pause', help='Pozastaví přehrávání písně')
async def pause(ctx):
    voice_channel = ctx.guild.voice_client
    if voice_channel.is_playing():  
        voice_channel.pause()                                                    # Pozastaví přehrávání písně
        await ctx.send("Píseň pozastavena")                                      # Odešle zprávu s potvrzením pozastavení přehrávání
    else:    
        await ctx.send("Bot v současné době nic nepřehrává.")                    # Odešle zprávu, pokud bot v současné době nic nepřehrává

@bot.command(name='resume', help='Obnoví přehrávání písně')
async def resume(ctx):    
    voice_channel = ctx.guild.voice_client
    if voice_channel.is_paused(): 
        voice_channel.resume()                                                   # Obnoví přehrávání písně
        await ctx.send("Píseň byla obnovena")                                    # Odešle zprávu s potvrzením obnovení přehrávání
    else:
        await ctx.send("Bot před tímto nepřehrával nic. Použijte příkaz !play")  # Odešle zprávu, pokud bot nepřehrával předtím

bot.run("TOKEN MÍSTO TEXTU")  # Spustí bota s předaným tokenem
