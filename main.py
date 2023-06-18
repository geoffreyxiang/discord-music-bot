import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import os


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# All the music-related stuff
is_playing = False
is_paused = False

# 2D array containing [song, channel]
music_queue = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

vc = None

#remove the default help command so that we can write out own
bot.remove_command('help')

#register the class with the bot
# bot.add_cog(music_cog(bot))
# bot.add_cog(help_cog(bot))

text_channel_list = []
help_message = """
```
General commands:
/help - displays all the available commands
/p <keywords> - finds the song on youtube and plays it in your current channel. Will resume playing the current song if it was paused
/q - displays the current music queue
/skip - skips the current song being played
/clear - Stops the music and clears the queue
/leave - Disconnected the bot from the voice channel
/pause - pauses the current song being played or resumes if already paused
/resume - resumes playing the current song
```
"""    

@bot.command(name="help", help="Displays all the available commands")
async def help(ctx):
    await ctx.send(help_message)

async def send_to_all(msg):
    for text_channel in text_channel_list:
        await text_channel.send(msg)

# Searching the item on YouTube
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except Exception:
            return False

    # return {'source': info['formats'][0]['url'], 'title': info['title']}
    return {'source': info['url'], 'title': info['title']}

def play_next():
    global is_playing
    global music_queue
    if len(music_queue) > 0:
        is_playing = True

        # Get the first URL
        m_url = music_queue[0][0]['source']

        # Remove the first element as you are currently playing it
        music_queue.pop(0)

        vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next())
    else:
        is_playing = False

# Infinite loop checking
async def play_music(ctx):
    global is_playing
    global music_queue
    if len(music_queue) > 0:
        is_playing = True

        m_url = music_queue[0][0]['source']

        global vc
        # Try to connect to the voice channel if you are not already connected
        if vc is None or not vc.is_connected():
            vc = await music_queue[0][1].connect()

            # In case we fail to connect
            if vc is None:
                await ctx.send("Could not connect to the voice channel")
                return
        else:
            await vc.move_to(music_queue[0][1])

        # Remove the first element as you are currently playing it
        music_queue.pop(0)

        vc.play(discord.FFmpegPCMAudio(m_url, **FFMPEG_OPTIONS), after=lambda e: play_next())
    else:
        is_playing = False

@bot.command(name="play", aliases=["p", "playing"], help="Plays a selected song from YouTube")
async def play(ctx, *args):
    global is_playing
    global is_paused
    query = " ".join(args)

    voice_channel = ctx.message.author.voice.channel
    if voice_channel is None:
        # You need to be connected so that the bot knows where to go
        await ctx.send("Connect to a voice channel!")
    elif is_paused:
        vc.resume()
    else:
        song = search_yt(query)
        if type(song) == type(True):
            await ctx.send(
                "Could not download the song. Incorrect format, try another keyword. "
                "This could be due to a playlist or a livestream format."
            )
        else:
            await ctx.send("Song added to the queue")
            music_queue.append([song, voice_channel])

            if not is_playing:
                await play_music(ctx)

@bot.command(name="pause", help="Pauses the current song being played")
async def pause(ctx, *args):
    global is_playing
    global is_paused
    if is_playing:
        is_playing = False
        is_paused = True
        vc.pause()
    elif is_paused:
        is_paused = False
        is_playing = True
        vc.resume()

@bot.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
async def resume(ctx, *args):
    global is_playing
    global is_paused
    if is_paused:
        is_paused = False
        is_playing = True
        vc.resume()

@bot.command(name="skip", aliases=["s"], help="Skips the current song being played")
async def skip(ctx):
    if vc != None and vc:
        vc.stop()
        #try to play next in the queue if it exists
        await play_music(ctx)


@bot.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
async def queue(ctx):
    global music_queueu
    retval = ""
    for i in range(0, len(music_queue)):
        # display a max of 5 songs in the current queue
        if (i > 4): break
        retval += music_queue[i][0]['title'] + "\n"

    if retval != "":
        await ctx.send(retval)
    else:
        await ctx.send("No music in queue")

@bot.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
async def clear(ctx):
    global music_queue
    if vc != None and is_playing:
        vc.stop()
    music_queue = []
    await ctx.send("Music queue cleared")

@bot.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
async def dc(ctx):
    global is_playing
    global is_paused
    is_playing = False
    is_paused = False
    await vc.disconnect()

#start the bot with our token
# bot.run(str(os.getenv("TOKEN")))
bot.run("MTExOTg0MjY4MTU5ODc4NzY5Ng.GUiFqi.xHw2LkI3LBEFrNjfPTrtnnxT_ElPRKgDrN4akQ")