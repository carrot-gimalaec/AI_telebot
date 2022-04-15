import telebot
from pyzbar import pyzbar
import cv2
import requests
from datetime import datetime
import time

def get_otch(key):
    time_now = datetime.today().strftime("%Y-%m-%d")
    data = {"dateFrom": time_now,
            "key": key}
    res = requests.get('https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks', params=data)
    r_json = res.json()
    print(r_json)
    return r_json
def draw_barcode(decoded, image):
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top),
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image

bot = telebot.TeleBot("your_token_tg_bot")
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Введите свой API')
@bot.message_handler(content_types=['text'])
def begin(message):
    time_now = datetime.today().strftime("%Y-%m-%d")
    key = message.text
    data = {"dateFrom": time_now,
            "key": key}
    res = requests.get('https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks', params=data)
    rsc=res.status_code
    if rsc == 200:
        bot.send_message(message.chat.id, 'Успешно, можете отправлять штрихкод')

        @bot.message_handler(content_types=['photo'])
        def photo (message):
            #print(message.photo)
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('photo.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
            image = cv2.imread('photo.jpg', 0)
            decoded_objects = pyzbar.decode(image)
            b = str
            for obj in decoded_objects:
                b = obj.data
                img = draw_barcode(obj, image)
            cv2.imwrite("photo1.jpg", img)
            a = []
            for p in range(len(b)):
                k = b[p]
                a.append(chr(k))
            print(a)
            barcode = "".join(a)
            bot.send_message(message.chat.id, 'Подождите, пожалуйста...')
            time.sleep(30)
            r_json = get_otch(key)
            dick = {}
            for i in r_json:
                for j in i.values():
                    if (j == barcode):
                        dick = i
            print(dick)
            if (len(dick) > 0):
                num = dick['supplierArticle']
                names1 = dick['subject']
                num1 = dick['nmId']
                brand = dick['brand']
                bot.send_message(message.chat.id, f"Артикул:  {num}\nНазвание:  {names1}\nАртикул WB:  {num1}\nБренд: {brand}")
                photo2 = open('photo1.jpg', 'rb')
                bot.send_photo(message.chat.id, photo2)
            else:
                bot.send_message(message.chat.id, "Товар не найден")
    else:
        bot.send_message(message.chat.id, 'Ошибка, неправильный API')

bot.polling( none_stop = True)