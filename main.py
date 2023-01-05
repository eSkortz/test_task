from googletrans import Translator
import telebot
from telebot import types
import requests as r
import json
import sqlite3
import random

bot = telebot.TeleBot('5848497570:AAGTkKgKwZ52mNkoakXDoXfMluxLXVWTakQ')


def resource_request():
    rg = r.get('https://jsonplaceholder.typicode.com/posts')
    data = json.loads(rg.text)
    return data


@bot.message_handler(content_types=['text', 'audio', 'document', 'photo'])
@bot.message_handler(commands=['start'])
def start(message):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(userid INT PRIMARY KEY, actions_number INT, language TEXT);""")
    db.commit()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    pointer = 0
    for i in range(len(users)):
        if users[i][0] == message.chat.id:
            pointer = 1
    if pointer == 0:
        new_user = (message.chat.id, 0, 'en')
        cur.execute("INSERT INTO users VALUES(?, ?, ?);", new_user)
        db.commit()
    markup_inline = types.InlineKeyboardMarkup()
    random_post_button = types.InlineKeyboardButton('🧨 View random post', callback_data=f'See random post|yes')
    see_all_posts_button = types.InlineKeyboardButton('🗂 Viewing the list of posts',
                                                      callback_data='See all posts|0|yes')
    en = types.InlineKeyboardButton('🇬🇧', callback_data='Switch to English')
    ru = types.InlineKeyboardButton('🇷🇺', callback_data='Switch to Russian')
    de = types.InlineKeyboardButton('🇩🇪', callback_data='Switch to German')
    markup_inline.add(random_post_button)
    markup_inline.add(see_all_posts_button)
    markup_inline.add(en, ru, de)
    bot.send_message(message.chat.id, '🙈 Hey I have some posts for you, what would you like to view',
                     reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    translator = Translator()
    calling_data = call.data.split('|')

    if calling_data[0] == 'main':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        cur.execute("SELECT * FROM users;")
        all_results = cur.fetchall()
        for i in range(len(all_results)):
            if all_results[i][0] == call.message.chat.id:
                d_lang = all_results[i][2]

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if calling_data[0] == 'See all posts':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        cur.execute("SELECT * FROM users;")
        all_results = cur.fetchall()
        for i in range(len(all_results)):
            if all_results[i][0] == call.message.chat.id:
                d_lang = all_results[i][2]

        posts = resource_request()
        page_id = int(calling_data[1])
        from_main_point = calling_data[2]
        result = translator.translate(f'Next page', src='en', dest=d_lang)
        if page_id + 10 >= len(posts):
            end_point = len(posts)
            next_page_button = types.InlineKeyboardButton(f'{result.text} ➡️', callback_data=f'See all posts|0|no')
        else:
            end_point = page_id + 10
            next_page_button = types.InlineKeyboardButton(f'{result.text} ➡️',
                                                          callback_data=f'See all posts|{end_point}|no')
        result = translator.translate(f'Previous page', src='en', dest=d_lang)
        if page_id - 10 < 0:
            previous_page_button = types.InlineKeyboardButton(f'⬅️ {result.text}',
                                                              callback_data=f'See all posts|{len(posts) - 10}|no')
        else:
            previous_page_button = types.InlineKeyboardButton(f'⬅️ {result.text}',
                                                              callback_data=f'See all posts|{page_id - 10}|no')
        markup_inline = types.InlineKeyboardMarkup()
        for i in range(page_id, end_point):
            result = translator.translate(f'{posts[i]["title"]}', src='la', dest=d_lang)
            markup_inline.add(types.InlineKeyboardButton(f'📰 {result.text[0].upper()}{result.text[1:]}',
                                                         callback_data=f'See post|{i}|{page_id}'))
        markup_inline.add(previous_page_button, next_page_button)
        result = translator.translate(f'Back to main menu', src='en', dest=d_lang)
        markup_inline.add(types.InlineKeyboardButton(f'🔙 {result.text}', callback_data='main'))
        result = translator.translate(f'List of posts', src='en', dest=d_lang)
        if from_main_point == 'yes':
            bot.send_message(call.message.chat.id, f'🗂 {result.text} {page_id + 1} - {end_point}',
                             reply_markup=markup_inline)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'🗂 {result.text} {page_id + 1} - {end_point}')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup_inline)
    if calling_data[0] == 'See post':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        cur.execute("SELECT * FROM users;")
        all_results = cur.fetchall()
        for i in range(len(all_results)):
            if all_results[i][0] == call.message.chat.id:
                d_lang = all_results[i][2]

        post_id = int(calling_data[1])
        page_id = calling_data[2]
        posts = resource_request()
        markup_inline = types.InlineKeyboardMarkup(row_width=1)
        result = translator.translate(f'Back to posts list', src='en', dest=d_lang)
        markup_inline.add(types.InlineKeyboardButton(f'🔙 {result.text}', callback_data=f'See all posts|{page_id}|no'))
        result = translator.translate(f'{posts[post_id]["title"]}', src='la', dest=d_lang)
        result1 = translator.translate(f'{posts[post_id]["body"]}', src='la', dest=d_lang)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'{result.text[0].upper()}{result.text[1:]}\n'
                                   f'\n{result1.text[0].upper()}{result1.text[1:]}')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup_inline)
    if calling_data[0] == 'See random post':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        cur.execute("SELECT * FROM users;")
        all_results = cur.fetchall()
        for i in range(len(all_results)):
            if all_results[i][0] == call.message.chat.id:
                d_lang = all_results[i][2]

        from_main_point = calling_data[1]
        posts = resource_request()
        post_id = random.randint(0, len(posts) - 1)
        markup_inline = types.InlineKeyboardMarkup(row_width=1)
        result = translator.translate(f'Next post', src='en', dest=d_lang)
        result1 = translator.translate(f'Back to main menu', src='en', dest=d_lang)
        markup_inline.add(types.InlineKeyboardButton(f'♻️ {result.text}', callback_data='See random post|no'),
                          types.InlineKeyboardButton(f'🔙 {result1.text}', callback_data='main'))
        result = translator.translate(f'{posts[post_id]["title"]}', src='la', dest=d_lang)
        result1 = translator.translate(f'{posts[post_id]["body"]}', src='la', dest=d_lang)
        if from_main_point == 'yes':
            bot.send_message(call.message.chat.id, f'{result.text[0].upper()}{result.text[1:]}\n'
                                                   f'\n{result1.text[0].upper()}{result1.text[1:]}',
                             reply_markup=markup_inline)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'{result.text[0].upper()}{result.text[1:]}\n'
                                       f'\n{result1.text[0].upper()}{result1.text[1:]}')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup_inline)

    if calling_data[0] == 'Switch to English':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET language = "en" WHERE userid = {call.message.chat.id}')
        db.commit()

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        markup_inline = types.InlineKeyboardMarkup()
        result = translator.translate(f'View random post', src='en', dest='en')
        random_post_button = types.InlineKeyboardButton(f'🧨 {result.text}', callback_data=f'See random post|yes')
        result = translator.translate(f'Viewing the list of posts', src='en', dest='en')
        see_all_posts_button = types.InlineKeyboardButton(f'🗂 {result.text}',
                                                          callback_data='See all posts|0|yes')
        en = types.InlineKeyboardButton('🇬🇧', callback_data='Switch to English')
        ru = types.InlineKeyboardButton('🇷🇺', callback_data='Switch to Russian')
        de = types.InlineKeyboardButton('🇩🇪', callback_data='Switch to German')
        markup_inline.add(random_post_button)
        markup_inline.add(see_all_posts_button)
        markup_inline.add(en, ru, de)

        result = translator.translate(f'Hey I have some posts for you, what would you like to view', src='en',
                                      dest='en')
        bot.send_message(call.message.chat.id, f'🙈 {result.text}', reply_markup=markup_inline)
    if calling_data[0] == 'Switch to Russian':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET language = "ru" WHERE userid = {call.message.chat.id}')
        db.commit()

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        markup_inline = types.InlineKeyboardMarkup()
        result = translator.translate(f'View random post', src='en', dest='ru')
        random_post_button = types.InlineKeyboardButton(f'🧨 {result.text}', callback_data=f'See random post|yes')
        result = translator.translate(f'Viewing the list of posts', src='en', dest='ru')
        see_all_posts_button = types.InlineKeyboardButton(f'🗂 {result.text}',
                                                          callback_data='See all posts|0|yes')
        en = types.InlineKeyboardButton('🇬🇧', callback_data='Switch to English')
        ru = types.InlineKeyboardButton('🇷🇺', callback_data='Switch to Russian')
        de = types.InlineKeyboardButton('🇩🇪', callback_data='Switch to German')
        markup_inline.add(random_post_button)
        markup_inline.add(see_all_posts_button)
        markup_inline.add(en, ru, de)

        result = translator.translate(f'Hey I have some posts for you, what would you like to view', src='en',
                                      dest='ru')
        bot.send_message(call.message.chat.id, f'🙈 {result.text}', reply_markup=markup_inline)
    if calling_data[0] == 'Switch to German':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET language = "de" WHERE userid = {call.message.chat.id}')
        db.commit()

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        markup_inline = types.InlineKeyboardMarkup()
        result = translator.translate(f'View random post', src='en', dest='de')
        random_post_button = types.InlineKeyboardButton(f'🧨 {result.text}', callback_data=f'See random post|yes')
        result = translator.translate(f'Viewing the list of posts', src='en', dest='de')
        see_all_posts_button = types.InlineKeyboardButton(f'🗂 {result.text}',
                                                          callback_data='See all posts|0|yes')
        en = types.InlineKeyboardButton('🇬🇧', callback_data='Switch to English')
        ru = types.InlineKeyboardButton('🇷🇺', callback_data='Switch to Russian')
        de = types.InlineKeyboardButton('🇩🇪', callback_data='Switch to German')
        markup_inline.add(random_post_button)
        markup_inline.add(see_all_posts_button)
        markup_inline.add(en, ru, de)

        result = translator.translate(f'Hey I have some posts for you, what would you like to view', src='en',
                                      dest='de')
        bot.send_message(call.message.chat.id, f'🙈 {result.text}', reply_markup=markup_inline)


bot.polling(none_stop=True, timeout=0)
