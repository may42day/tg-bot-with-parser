import telebot
import sqlite3
import time

bot_token = '5193323572:AAGhIY6dO1N1lhdOx1yLGE5YgLFVVHVU8o0'
bot = telebot.TeleBot(bot_token, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "/start":
        add_user_into_db(message.from_user.id)
        bot.send_message(message.from_user.id, f"Твой id добавлен {message.from_user.id}")


def add_user_into_db(user_id):
    conn = sqlite3.connect('users_db.db')
    cur = conn.cursor()

    if cur.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE user_id={user_id})").fetchall()[0][0] == 0:
        cur.execute(f"INSERT INTO users (user_id) VALUES ({user_id})")

    conn.commit()
    conn.close()  


def creating_users_DB():
    conn = sqlite3.connect('users_db.db')
    cur = conn.cursor()
        
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users'")
    if cur.fetchone()[0] != 1 :
        cur.execute("CREATE TABLE users (user_id INTEGER)")

    conn.commit()
    conn.close()


def message_new_flats_for_all_users(flats_list):
    conn = sqlite3.connect('users_db.db')
    cur = conn.cursor()
    all_users_list = cur.execute("SELECT * FROM users").fetchall()

    for user in all_users_list:
        for flat in flats_list:
            bot.send_photo(user[0], photo=flat[5], caption=list_item_into_message(flat))
        time.sleep(1)
    conn.commit()
    conn.close()  


def list_item_into_message(list_item):
    header = list_item[0]
    place = list_item[1]
    price = list_item[2]
    rooms = list_item[3]
    square = list_item[4]
    link = list_item[6]
    return f"<b>{header}</b>\n\nPlace: {place}\nPrice: {price}\n{rooms}, {square}\nlink:{link}"


def main():
    creating_users_DB()
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except: 
            print('Bot shutdown')


if __name__ == '__main__':
    main()