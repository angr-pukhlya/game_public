import logging
import random
import telegram
from handlers import stats
import os

logger = logging.getLogger()
countries_caps = {'Albania': 'Tirana', 'Andorra': 'Andorra la Vella', 'Austria': 'Vienna', 'Belarus': 'Minsk',
                  'Belgium': 'Brussels', 'Bulgaria': 'Sofia', 'Bosnia and Herzegovina': 'Sarajevo',
                  'Denmark': 'Copenhagen', 'Germany': 'Berlin', 'Greece': 'Athens', 'Hungary': 'Budapest',
                  'Iceland': 'Reykjavik', 'Ireland': 'Dublin', 'Italy': 'Rome', 'Latvia': 'Riga',
                  'Liechtenstein': 'Vaduz', 'Lithuania': 'Vilnius', 'Luxembourg': 'Luxembourg', 'Malta': 'Valletta',
                  'Moldova': 'Kishinev', 'Monaco': 'Monaco', 'Netherlands': 'Amsterdam', 'Norway': 'Oslo',
                  'Poland': 'Warsaw', 'Portugal': 'Lisbon', 'Romania': 'Bucharest', 'The Russian Federation': 'Moscow',
                  'San Marino': 'San Marino', 'Serbia': 'Belgrade', 'Slovakia': 'Bratislava', 'Slovenia': 'Ljubljana',
                  'Spain': 'Madrid', 'Sweden': 'Stockholm', 'Switzerland': 'Bern', 'The United Kingdom': 'London',
                  'Finland': 'Helsinki', 'Estonia': 'Tallinn', 'The Czech Republic': 'Prague', 'Montenegro': 'Podgorica',
                  'France': 'Paris', 'North Macedonia': 'Skopje', 'Ukraine': 'Kiev', 'Croatia': 'Zagreb'}
all_countries = list(countries_caps.keys())
zoom = {'Monaco', 'Liechtenstein'}
LEN_A_C = len(all_countries)
users = dict()


class State:
    def __init__(self, params=None, countries=None):
        if params is None:
            params = {'guessed': 0, 'right': '', 'level': LEN_A_C, 'set': False,
                      'started': False, 'mode': 'country', 'set_mode': False}
            countries = all_countries.copy()
            random.shuffle(countries)
        self.guessed = params['guessed']
        self.right = params['right']
        self.level = params['level']
        self.set = params['set']
        self.started = params['started']
        self.mode = params['mode']
        self.set_mode = params['set_mode']
        self.countries = countries


@stats.handler
def set_mode(update, context):
    user_id = update.effective_chat.id
    if user_id not in users or user_id in users and not users[user_id].started:
        ans = 'Firstly, start a new game - /game'
        context.bot.send_message(user_id, ans)
    else:
        msg = update.message.text.lower()[6:]
        if msg != 'country' and msg != 'capital':
            md = ['country', 'capital'][random.randint(0, 1)]
            ans = 'There is no mode \'{}\'! Please choose \'country\' or \'capital\', e.g. /mode {}'.format(msg, md)
            context.bot.send_message(user_id, ans)
        else:
            users[user_id].mode, users[user_id].set_mode, users[user_id].started = msg, True, True
            context.bot.send_message(user_id, 'Great! Now choose the number '
                                              'of rounds (1 <= x <= {}) - /level x'.format(LEN_A_C))


@stats.handler
def set_level(update, context):
    user_id = update.effective_chat.id
    if user_id not in users or user_id in users and not users[user_id].started:
        ans = 'Firstly, start a new game - /game'
        context.bot.send_message(user_id, ans)
    elif not users[user_id].set_mode:
        ans = 'Choose the mode first - /mode'
        context.bot.send_message(user_id, ans)
    else:
        msg = update.message.text[7:]
        num = random.randint(1, LEN_A_C)
        if not msg.isdigit():
            ans = '{} is not a number! Please type something like this: /level {}'.format(msg, num)
            context.bot.send_message(user_id, ans)
        else:
            level = int(msg)
            if level < 1 or level > LEN_A_C:
                context.bot.send_message(user_id,
                                         'Choose the number between 1 and {}, e.g. {}'.format(LEN_A_C, num))
            else:
                users[user_id].level, users[user_id].set, users[user_id].started = level, True, True
                context.bot.send_message(user_id, 'Cool! Let\'s start then')
                send_picture(update, context)


@stats.handler
def send_picture(update, context):
    user_id = update.effective_chat.id
    users[user_id].right = users[user_id].countries.pop()
    path = 'media/{}'.format(users[user_id].right + '.png')
    if users[user_id].right not in zoom:
        context.bot.send_photo(user_id, photo=open(path, 'rb'),
                               caption='Guess the {}'.format(users[user_id].mode))
    else:
        cap = 'Guess the {}\n/zoom - There is zoomed out picture'.format(users[user_id].mode)
        context.bot.send_photo(user_id, photo=open(path, 'rb'), caption=cap)


@stats.handler
def send_zoom(update, context):
    user_id = update.effective_chat.id
    if user_id not in users or user_id in users and not users[user_id].started:
        ans = 'Firstly, start a new game - /game'
        context.bot.send_message(user_id, ans)
    elif not users[user_id].set:
        ans = 'Choose the number of rounds - /level'
        context.bot.send_message(user_id, ans)
    elif not users[user_id].set_mode:
        ans = 'Choose the mode first - /mode'
        context.bot.send_message(user_id, ans)
    elif users[user_id].right in zoom:
        path = 'media/{}'.format(users[user_id].right + '2.png')
        context.bot.send_photo(user_id, photo=open(path, 'rb'))
    else:
        context.bot.send_message(user_id, 'There isn\'t zoomed out picture of this country')


@stats.handler
def answer(update, context):
    user_id = update.effective_chat.id
    msg = update.message.text.lower()
    if user_id not in users or user_id in users and not users[user_id].started:
        ans = 'Firstly, start a new game - /game'
    elif not users[user_id].set_mode:
        ans = 'Choose the mode first - /mode'
    elif not users[user_id].set:
        ans = 'Choose the number of rounds - /level'
    else:
        k = i = 0
        guess = ''
        if users[user_id].mode == 'country':
            right = users[user_id].right
        else:
            right = countries_caps[users[user_id].right]
        while i < LEN_A_C and k < 2 and guess.lower() != right.lower():
            if users[user_id].mode == 'country':
                r = all_countries[i].lower()
            else:
                r = countries_caps[all_countries[i]].lower()
            if r in msg:
                k += 1
                guess = r
            i += 1
        if k == 1 and guess.lower() == right.lower():
            ans = 'Yep!'
            users[user_id].guessed += 1
        elif k <= 1:
            ans = 'Nope. The answer is {}'.format(right)
        else:
            ans = 'Name only one {}, you little cheater'.format(users[user_id].mode)
    context.bot.send_message(user_id, ans)
    if ans[0] == 'Y' or ans[:2] == 'No':
        if len(users[user_id].countries) != LEN_A_C - users[user_id].level:
            send_picture(update, context)
        else:
            if users[user_id].guessed < users[user_id].level / 2:
                ans = 'Oh no!'
            else:
                ans = 'Yay!'
            ans += ' Result: {}/{}'.format(users[user_id].guessed, users[user_id].level)
            ans += '\n/game - If you want to start a new game'
            renew(update)
            context.bot.send_message(user_id, ans)


def renew(update):
    users[update.effective_chat.id] = State()


@stats.handler
def start(update, context):
    user_id = update.effective_chat.id
    renew(update)
    ans = 'Choose the mode - /mode capital or /mode country'
    users[user_id].started = True
    context.bot.send_message(user_id, ans)


@stats.handler
def stop(update, context):
    user_id = update.effective_chat.id
    if user_id not in users or user_id in users and not users[user_id].started:
        ans = '''You haven't even started the game and you already want to stop :'c
/game - if you want to start a game again...'''
    else:
        ans = 'I stopped the game.'
        renew(update)
    context.bot.send_message(user_id, ans)
