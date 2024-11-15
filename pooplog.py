import discord
from discord.ext import commands
import datetime
import sqlite3
from typing import List

# Set up bot with command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
def setup_database():
    conn = sqlite3.connect('poop_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS poops
                 (user_id TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Helper function to get formatted timestamps
def get_discord_timestamp(dt: datetime.datetime) -> str:
    unix_timestamp = int(dt.timestamp())
    return f"<t:{unix_timestamp}:R>"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    setup_database()

@bot.command(name='poop')
async def log_poop(ctx):
    conn = sqlite3.connect('poop_log.db')
    c = conn.cursor()
    current_time = datetime.datetime.now()
    c.execute('INSERT INTO poops VALUES (?, ?)', (str(ctx.author.id), current_time))
    conn.commit()
    conn.close()
    
    await ctx.send("Emi just took a poop! 💩")

@bot.command(name='lastpoop')
async def last_poop(ctx):
    conn = sqlite3.connect('poop_log.db')
    c = conn.cursor()
    c.execute('SELECT timestamp FROM poops WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', 
              (str(ctx.author.id),))
    result = c.fetchone()
    conn.close()
    
    if result:
        last_poop_time = datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
        discord_timestamp = get_discord_timestamp(last_poop_time)
        await ctx.send(f"Emi's last poop was {discord_timestamp}")
    else:
        await ctx.send("No poops logged yet!")

@bot.command(name='pooplog')
async def poop_log(ctx):
    conn = sqlite3.connect('poop_log.db')
    c = conn.cursor()
    c.execute('SELECT timestamp FROM poops WHERE user_id = ? ORDER BY timestamp DESC LIMIT 15',
              (str(ctx.author.id),))
    results = c.fetchall()
    conn.close()
    
    if not results:
        await ctx.send("No poops logged yet!")
        return
    
    embed = discord.Embed(title="Emi's Poop Log", 
                         description="Your last 15 poops:",
                         color=0x964B00)
    
    for i, result in enumerate(results, 1):
        poop_time = datetime.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
        discord_timestamp = get_discord_timestamp(poop_time)
        embed.add_field(name=f"Poop #{i}", value=discord_timestamp, inline=False)
    
    await ctx.send(embed=embed)

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
bot.run('')
