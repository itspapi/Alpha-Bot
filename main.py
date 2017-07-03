import discord
from discord.ext import commands
import json
import sys
import os
from utils import prettyoutput as po

bot = commands.Bot(command_prefix="")
config = None

def update_file():
  with open('config.json', 'w') as fileOut:
    json.dump(config, fileOut, indent=2, sort_keys=True)

def import_config():
  global config
  try:
    print(po.info(string="Importing configuration...", prn_out=False))
    with open('config.json', 'r') as file_in:
      config = json.load(file_in)
  except FileNotFoundError:
    print(po.error(string="Config file not found, creating...", prn_out=False))
    with open('config.json', 'w+') as file_out:
      config_temp = {"token": "", "admin_ids": [""], "servers": [{}]}
      json.dump(config_temp, file_out, indent=2, sort_keys=True)
    print(po.error(string="Please put your bot's token in the 'token' key in config.json", prn_out=False))
    sys.exit()

def add_cogs():
  print(po.info(string="Getting all extensions in the cogs folder...", prn_out=False))
  startup_extensions = []
  for cog in os.popen('ls cogs/').read().split('\n'):
    if not cog == "":
      startup_extensions.append("cogs." + cog.split('.')[0])
  return startup_extensions

@bot.event
async def on_ready():
  global config
  print(po.success(string='Logged into discord', prn_out=False))
  print(bot.user.name + "#" + bot.user.discriminator)
  print(bot.user.id)
  print('------')
  if not config['log_channel_id'] == "":
    try:
      print('Console messages will be send to channel #{} ({}) in {} ({})'.format(bot.get_channel(config['log_channel_id']).name, bot.get_channel(config['log_channel_id']).id, bot.get_channel(config['log_channel_id']).server.name, bot.get_channel(config['log_channel_id']).server.id))
    except AttributeError:
      print(po.error(string='The bot could not access the log channel', prn_out=False))

  await bot.change_presence(game=discord.Game(name='Alpha Bot indev'))

  for extension in add_cogs():
    print(po.info(string="Loading {}...".format(extension), prn_out=False))
    try:
      bot.load_extension(extension)
    except Exception as e:
      exc = '{}: {}'.format(type(e).__name__, e)
      print(po.error(string='Failed to load extension {}\n{}'.format(extension, exc), prn_out=False))
  print(po.success(string="All extensions loaded successfully", prn_out=False))


@bot.event
async def on_message(message):
  await bot.process_commands(message)

# defined here so it can't be accidentally unloaded
@bot.command(name="reload", hidden=True, pass_context=True)
async def reload_module(ctx, module):
  if ctx.message.author.id == '135483608491229184' or ctx.message.author.id == '135496683009081345':
    bot.unload_extension(module)
    bot.load_extension(module)
    await bot.say("done")

if __name__ == '__main__':
  import_config()
  if config['log_channel_id'] == "":
    print("No log channel set, all status messages will be printed to the console.")
  try:
    bot.run(config['token'])
  except discord.errors.LoginFailure as e:
    print(po.error(string=str(e), prn_out=False))
    sys.exit()
  except Exception as e:
    print(po.error(string=type(e).__name__ + ": " + str(e), prn_out=False))
