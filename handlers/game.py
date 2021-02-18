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
                  'Poland': 'Warsaw', 'Portugal': 'Lisbon', 'Romania': 'Bucharest', 'Russian Federation': 'Moscow',
                  'San Marino': 'San Marino', 'Serbia': 'Belgrade', 'Slovakia': 'Bratislava', 'Slovenia': 'Ljubljana',
                  'Spain': 'Madrid', 'Sweden': 'Stockholm', 'Switzerland': 'Bern', 'United Kingdom': 'London',
                  'Finland': 'Helsinki', 'Estonia': 'Tallinn', 'Czech Republic': 'Prague', 'Montenegro': 'Podgorica',
                  'France': 'Paris', 'North Macedonia': 'Skopje', 'Ukraine': 'Kiev', 'Croatia': 'Zagreb'}
all_countries = list(countries_caps.keys())
# zoom = set([elem[:-5] for elem in os.listdir(path="media") if elem[-5] == '2'])
zoom = {'Monaco', 'Liechtenstein'}
LEN_A_C = len(all_countries)
params = {'guessed': 0, 'right': '', 'level': LEN_A_C, 'set': False, 'started': False, 'mode': 'country',
          'set_mode': False}
countries = all_countries.copy()
random.shuffle(countries)


@stats.handler
def set_mode(update, context):
    if not params['started']:
        ans = 'Firstly, start a new game - /game'
        context.bot.send_message(update.effective_chat.id, ans)
    else:
        msg = update.message.text.lower()[6:]
        if msg != 'country' and msg != 'capital':
            md = ['country', 'capital'][random.randint(0, 1)]
            ans = 'There is no mode \'{}\'! Please choose \'country\' or \'capital\', e.g. /mode {}'.format(msg, md)
            context.bot.send_message(update.effective_chat.id, ans)
        else:
            params['mode'], params['set_mode'], params['started'] = msg, True, True
            context.bot.send_message(update.effective_chat.id, 'Great! Now choose the number '
                                                               'of rounds (1 <= x <= {}) - /level x'.format(LEN_A_C))


@stats.handler
def set_level(update, context):
    if not params['started']:
        ans = 'Firstly, start a new game - /game'
        context.bot.send_message(update.effective_chat.id, ans)
    if not params['set_mode']:
        ans = 'Choose the mode first - /mode'
        context.bot.send_message(update.effective_chat.id, ans)
    else:
        msg = update.message.text[7:]
        num = random.randint(1, LEN_A_C)
        print(msg, msg.isdigit())
        if not msg.isdigit():
            ans = '{} is not a number! Please type something like this: /level {}'.format(msg, num)
            context.bot.send_message(update.effective_chat.id, ans)
        else:
            level = int(msg)
            if level < 1 or level > LEN_A_C:
                context.bot.send_message(update.effective_chat.id,
                                         'Choose the number between 1 and {}, e.g. {}'.format(LEN_A_C, num))
            else:
                params['level'], params['set'], params['started'] = level, True, True
                context.bot.send_message(update.effective_chat.id, 'Cool! Let\'s start then')
                send_picture(update, context)


@stats.handler
def send_picture(update, context):
    params['right'] = countries.pop()
    print(params['right'])
    path = 'media/{}'.format(params['right'] + '.png')
    if params['right'] not in zoom:
        context.bot.send_photo(update.effective_chat.id, photo=open(path, 'rb'),
                               caption='Guess the {}'.format(params['mode']),
                               parse_mode=telegram.ParseMode.MARKDOWN_V2)
    else:
        cap = '''Guess the name
/zoom - There is zoomed out picture'''
        context.bot.send_photo(update.effective_chat.id, photo=open(path, 'rb'),
                               caption=cap, parse_mode=telegram.ParseMode.MARKDOWN_V2)


def send_zoom(update, context):
    if not params['started']:
        ans = 'Firstly, start a new game - /game'
        context.bot.send_message(update.effective_chat.id, ans)
    elif not params['set']:
        ans = 'Choose the number of rounds - /level'
        context.bot.send_message(update.effective_chat.id, ans)
    elif not params['set_mode']:
        ans = 'Choose the mode first - /mode'
        context.bot.send_message(update.effective_chat.id, ans)
    elif params['right'] in zoom:
        path = 'media/{}'.format(params['right'] + '2.png')
        print(path)
        context.bot.send_photo(update.effective_chat.id, photo=open(path, 'rb'),
                               parse_mode=telegram.ParseMode.MARKDOWN_V2)
    else:
        context.bot.send_message(update.effective_chat.id, 'There isn\'t zoomed out picture of this country')


@stats.handler
def answer(update, context):
    msg = update.message.text.lower()
    print(params, 'hoy')
    if not params['started']:
        ans = 'Firstly, start a new game - /game'
        print(params, 'hi')
    elif not params['set_mode']:
        ans = 'Choose the mode first - /mode'
    elif not params['set']:
        ans = 'Choose the number of rounds - /level'
    else:
        k = i = 0
        guess = ''
        if params['mode'] == 'country':
            right = params['right'].lower()
        else:
            right = countries_caps[params['right']].lower()
        while i < LEN_A_C and k < 2 and guess != right:
            if params['mode'] == 'country':
                r = all_countries[i].lower()
            else:
                r = countries_caps[all_countries[i]].lower()
            if r in msg:
                print(all_countries[i], guess)
                k += 1
                guess = r
            i += 1
        if k == 1 and guess.lower() == right.lower():
            ans = 'Yep!'
            params['guessed'] += 1
        elif k <= 1:
            print(guess, params['right'], guess == params['right'], k)
            ans = 'Nope. The answer is {}'.format(right.capitalize())
        else:
            ans = 'Name only one {}, you little cheater'.format(params['mode'])
    context.bot.send_message(update.effective_chat.id, ans)
    if ans[0] == 'Y' or ans[:2] == 'No':
        if len(countries) != LEN_A_C - params['level']:
            send_picture(update, context)
        else:
            if params['guessed'] < params['level'] / 2:
                ans = 'Oh no!'
            else:
                ans = 'Yay!'
            ans += ' Result: {}/{}'.format(params['guessed'], params['level'])
            ans += '\n/game - If you want to start a new game'
            renew()
            context.bot.send_message(update.effective_chat.id, ans)


def renew():
    params['guessed'], params['right'], params['level'], params['mode'] = 0, '', LEN_A_C, 'country'
    params['set_mode'] = params['set'] = params['started'] = False
    countries[:] = all_countries
    random.shuffle(countries)


def start(update, context):
    renew()
    ans = 'Choose the mode - /mode capital or /mode country'
    params['started'] = True
    context.bot.send_message(update.effective_chat.id, ans)


def stop(update, context):
    if not params['started']:
        ans = '''You haven't even started the game and you already want to stop :'c
/game - if you want to start a game again...'''
    else:
        ans = 'I stopped the game.'
        renew()
    context.bot.send_message(update.effective_chat.id, ans)
