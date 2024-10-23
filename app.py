import discord
from discord.ext import commands
from apify_client import ApifyClient
import asyncio, re
import traceback

TOKEN = 'BOT_TOKEN'

client = ApifyClient("apify_api")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('Bot is ready and connected to Discord!')

@bot.command(name="add")
async def addition(ctx, *numbers: str):
    try:
        total = sum(map(int, numbers))
        await ctx.send(f"The sum is: {total}")
    except ValueError:
        await ctx.send("Please provide only numbers.")

@bot.command(name="subtract")
async def subtraction(ctx, *numbers: str):
    if not numbers:
        await ctx.send("Please provide at least one number.")
        return

    try:
        # Convert the first number to start the subtraction and subtract subsequent numbers
        total = int(numbers[0]) - sum(map(int, numbers[1:]))
        await ctx.send(f"The result is: {total}")
    except ValueError:
        await ctx.send("Please provide only numbers.")

def parse_view_count(views):
    view_count_str = str(views)
    view_count_str = view_count_str.replace(',', '') 
    match = re.match(r'(\d+\.?\d*)([kKmM]?)', view_count_str)

    if match:
        number, suffix = match.groups()
        number = float(number)  
        if suffix.lower() == 'k':
            return int(number * 1_000) 
        elif suffix.lower() == 'm':
            return int(number * 1_000_000)  
        return int(number)   
    return 0 

def count_sync(instagram_username, reels):
    total_count = 0
    run_input = {
        "username": [instagram_username],
        "resultsLimit": reels
    }

    run = client.actor("frGcYk0meZkxxeo8k").call(run_input=run_input)

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        view = parse_view_count(item.get("videoPlayCount", 0))
        total_count += view

    return total_count

async def count_views(ctx, instagram_username: str, reels:int):
    try:
        instagram_username = instagram_username.strip()

        total_count = await asyncio.to_thread(count_sync, instagram_username, reels)

        await ctx.send(f"Total video play count for {instagram_username}: {total_count}")

    except Exception as e:
        await ctx.send("An error occurred!")
        traceback.print_exc()

@bot.command()
async def count(ctx, instagram_username: str, reels:int=63):
    async with ctx.channel.typing():
        await asyncio.create_task(count_views(ctx, instagram_username, reels))

bot.run(TOKEN)