import telebot
from telebot import types
import requests as r
import json
import sqlite3
import random

bot = telebot.TeleBot('')


def resource_request():
    rg = r.get('https://jsonplaceholder.typicode.com/posts')
    data = json.loads(rg.text)
    return data


@bot.message_handler(content_types=['text', 'audio', 'document', 'photo'])
@bot.message_handler(commands=['start'])
def start(message):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(userid INT PRIMARY KEY, actions_number INT KEY);""")
    db.commit()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    pointer = 0
    for i in range(len(users)):
        if users[i][0] == message.chat.id:
            pointer = 1
    print(pointer)
    if pointer == 0:
        new_user = (message.chat.id, 0)
        cur.execute("INSERT INTO users VALUES(?, ?);", new_user)
        db.commit()
    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    random_post_button = types.InlineKeyboardButton('🧨 View random post', callback_data=f'See random post|yes')
    see_all_posts_button = types.InlineKeyboardButton('🗂 Viewing the list of posts',
                                                      callback_data='See all posts|0|yes')
    markup_inline.add(random_post_button, see_all_posts_button)
    bot.send_message(message.chat.id, '🙈 Hey I have some posts for you, what would you like to view',
                     reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    calling_data = call.data.split('|')

    if calling_data[0] == 'main':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if calling_data[0] == 'See all posts':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        posts = resource_request()
        page_id = int(calling_data[1])
        from_main_point = calling_data[2]
        if page_id + 10 >= len(posts):
            end_point = len(posts)
            next_page_button = types.InlineKeyboardButton('Next page ➡️', callback_data=f'See all posts|0|no')
        else:
            end_point = page_id + 10
            next_page_button = types.InlineKeyboardButton('Next page ➡️', callback_data=f'See all posts|{end_point}|no')
        if page_id - 10 < 0:
            previous_page_button = types.InlineKeyboardButton('⬅️ Previous page',
                                                              callback_data=f'See all posts|{len(posts) - 10}|no')
        else:
            previous_page_button = types.InlineKeyboardButton('⬅️ Previous page',
                                                              callback_data=f'See all posts|{page_id - 10}|no')
        markup_inline = types.InlineKeyboardMarkup()
        for i in range(page_id, end_point):
            markup_inline.add(types.InlineKeyboardButton(f'📰 {posts[i]["title"][:20]}...',
                                                         callback_data=f'See post|{i}|{page_id}'))
        markup_inline.add(previous_page_button, next_page_button)
        markup_inline.add(types.InlineKeyboardButton('🔙 Back to main menu', callback_data='main'))
        if from_main_point == 'yes':
            bot.send_message(call.message.chat.id, f'🗂 List of posts {page_id + 1} - {end_point}',
                             reply_markup=markup_inline)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'🗂 List of posts {page_id + 1} - {end_point}')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup_inline)
    if calling_data[0] == 'See post':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        post_id = int(calling_data[1])
        page_id = calling_data[2]
        posts = resource_request()
        markup_inline = types.InlineKeyboardMarkup(row_width=1)
        markup_inline.add(types.InlineKeyboardButton('🔙 Back to posts list',
                                                     callback_data=f'See all posts|{page_id}|no'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'{posts[post_id]["title"]}\n\n{posts[post_id]["body"]}')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup_inline)

    if calling_data[0] == 'See random post':
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        cur.execute(f'UPDATE users SET actions_number = actions_number + 1 WHERE userid = {call.message.chat.id}')
        db.commit()

        from_main_point = calling_data[1]
        posts = resource_request()
        post_id = random.randint(0, len(posts) - 1)
        markup_inline = types.InlineKeyboardMarkup(row_width=1)
        markup_inline.add(types.InlineKeyboardButton('♻️ Next post', callback_data='See random post|no'),
                          types.InlineKeyboardButton('🔙 Back to main menu', callback_data='main'))
        if from_main_point == 'yes':
            bot.send_message(call.message.chat.id, f'{posts[post_id]["title"]}\n\n{posts[post_id]["body"]}',
                             reply_markup=markup_inline)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'{posts[post_id]["title"]}\n\n{posts[post_id]["body"]}')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup_inline)


bot.polling(none_stop=True, timeout=0)
