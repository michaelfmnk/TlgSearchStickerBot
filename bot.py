import telebot
from telebot import types
import settings as config
from pymongo import *

bot = telebot.TeleBot(config.key)
keys = config.data.keys()

client = MongoClient('localhost', 27017)
db = client["local"]
collection = db["stickers"]


@bot.inline_handler(lambda query: len(query.query) > 2)
def what(inline_query):
    try:
        result = collection.find({"title": {"$regex": u"" + inline_query.query.lower()}})
        answers = []
        i = 0
        for item in result:
            print(item["file_id"])
            answers.append(types.InlineQueryResultCachedSticker(str(i), sticker_file_id=item["file_id"]))
            i += 1
        print(answers)
        bot.answer_inline_query(inline_query.id, answers)

    except Exception as e:
        print(e)


def log(message):
    """ prints message-log """
    if True:
        from datetime import datetime
        print("\n ----------")

        print(datetime.now())
        print("NEW MESSAGE FROM {0} {1}. (id = {2}) (chatID = {3})\n TEXT  --- {4}".format(message.from_user.last_name,
                                                                                           message.from_user.first_name,
                                                                                           str(message.from_user.id),
                                                                                           str(message.chat.id),
                                                                                           message.text))


@bot.message_handler(content_types=['sticker'])
def print_sticker_id(sticker):
    if collection.find_one({"file_id": sticker.sticker.file_id}) is None:
        bot.send_message(sticker.chat.id, config.text_send_title + sticker.sticker.file_id,
                         reply_markup=types.ForceReply())
    else:
        bot.send_message(sticker.chat.id, "Данный стикер уже в базе данных")


@bot.message_handler(func=lambda m: m.reply_to_message is not None, content_types=['text', 'sticker', 'photo'])
def handler_title_for_sticker(message):
    if message.text is None:
        bot.send_message(message.chat.id, "Error")
        return

    if config.text_send_title in message.reply_to_message.text:
        sticker_id = message.reply_to_message.text[len(config.text_send_title):]
        sticker_title = message.text.lower()

        sticker_data = {'file_id': sticker_id, 'title': sticker_title}  # pack data and upload to mongoDB
        collection.insert_one(sticker_data)

        print("Added Sticker = " + sticker_id + "Title: " + message.text)  # logging
        bot.send_sticker("149036177", sticker_id)
        bot.send_message("149036177", "added new sticker id=" + sticker_id +
                         " title = " + sticker_title)


bot.polling(none_stop=True, interval=0)
