import logging
from handlers import game
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    help_message = '''
To start the game send the command /game
Then you will be given two options: you can either guess countries or capitals.
To choose first variant send /mode country, otherwise send /mode capital.
After that you will need to choose the amount of rounds (x), i.e. how many countries will be sent.
For this send /level x. That is all you need to start the game.
If you want to stop the game, send /stop.
There are zoomed out versions of some countries, so if you need them, send /zoom.
Send /help to see the list of commands.
❗️To copy the command from my messages, press on it for a second ❗'''
    context.bot.send_message(update.effective_chat.id, help_message)


def help_handler(update, context):
    help_msg = '''
/help - Show this message 
/start - Show the detailed instruction
/game - Start the game
/mode country or /mode capital - Guessing countries or capitals
/level x - Will be x rounds
/zoom - Get zoomed out picture (if there is one)
/stop - Stop the game'''
    context.bot.send_message(update.effective_chat.id, help_msg)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_handler))

dispatcher.add_handler(CommandHandler('game', game.start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, game.answer))
dispatcher.add_handler(CommandHandler('stop', game.stop))
dispatcher.add_handler(CommandHandler('zoom', game.send_zoom))
dispatcher.add_handler(CommandHandler('level', game.set_level))
dispatcher.add_handler(CommandHandler('mode', game.set_mode))

updater.start_polling()
