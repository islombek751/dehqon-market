from django.core.management.base import BaseCommand

import json

import os
import django
from django.core.checks import messages
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bozor.settings")
django.setup()  

import telebot
from telebot import types
from api.models import *

TOKEN = "5061556702:AAEX99Z-11f5OWDzeyb00KPUmT6FPlt_OjI"
chat_id = '-785780604'

bot = telebot.TeleBot(TOKEN,parse_mode='html',threaded=False)

category = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
for c in Category.objects.all():
    item_category = types.KeyboardButton(text=f"{c.title}")
    category.add(item_category)

@bot.message_handler(commands=['start'])
def kirish(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    reg_button = types.KeyboardButton(text="📞Telfon raqamni yuborish", request_contact=True)
    keyboard.add(reg_button)
    if not UserTelegram.objects.filter(telegram_id = message.chat.id):
        bot.send_message(message.chat.id,"Quyida so'ralgan ma'lumotlarni kiriting va ro'yhatdan o'ting!")
        response = bot.send_message(message.chat.id, 
                                "Iltimos, menyudagi tugma orqali telfon raqamingizni yuboring!", 
                                reply_markup=keyboard)
    # bot.register_next_step_handler(response,get_contact)
    else:
        sms = bot.send_message(message.chat.id,"Assalomu alaykum! Bu dehqonbozori.uz saytining telegram boti!\nMarhamat, kategoriyani tanlang!",reply_markup=category)
        bot.register_next_step_handler(sms,category_handler) 


number = ""
randomlist = ""
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    global number
    number = message.contact.phone_number
    if not UserTelegram.objects.filter(telegram_id = message.chat.id):
        import os
        from twilio.rest import Client
        account_sid = 'AC2617b089699004682ae2cae1e49095c1'
        auth_token = 'cb2ec0a058aa5795a7bb0596825397a0'
        client = Client(account_sid, auth_token)
        import random
        for i in range(0,5):
            n = random.randint(1,9)
            global randomlist
            randomlist+=str(n)
        mymessage = client.messages.create(to=f"+{number}", from_="+15865018320",
                                    body="Your Confirmation Code:\n"+randomlist)
        source = bot.send_message(message.chat.id,"Iltimos, sizga yuborilgan raqamli tasdiqlash kodini jo'nating!")
        bot.register_next_step_handler(source,confirmation)
    else:
        sms = bot.send_message(message.chat.id,"Siz allaqachon royhatdan o'tgansiz!",reply_markup=category)
        bot.register_next_step_handler(sms,category_handler) 


        
        
def confirmation(message):
    if message.text == randomlist:
        user = UserTelegram.objects.create(phone=number,otp = randomlist,telegram_id=message.chat.id)
        user.save()
        sms = bot.send_message(message.chat.id,"Ro'yhatdan o'tish muvaffaqiyatli yakunlandi!",reply_markup=category)
        bot.register_next_step_handler(sms,category_handler) 

    else:
        bot.send_message(message.chat.id,"Ro'yhatdan o'tishda hatolik yuz berdi!Siz notog'ri kod kiritdingiz!")


def category_handler(message):
    try:
        category_ttile = Category.objects.get(title = message.text)
        subcategory = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        for sc in Subcategory.objects.filter(category=category_ttile):
            item_category = types.KeyboardButton(text=f"{sc.title}")
            subcategory.add(item_category)
        sub_sms = bot.send_message(message.chat.id,"Iltimos, quyidagi subkategoriyalardan birini tanlang!",reply_markup=subcategory)
        bot.register_next_step_handler(sub_sms,subcategory_handler)
    except:
        pass

sub =None
product_sms = None
product = None


def knopka(message,sub_cat,usercart):
    global product
    product = types.InlineKeyboardMarkup()
    for sc in Product.objects.filter(category=sub_cat):
        price = sc.price if sc.sale == False else sc.price_in_sale
        item_product = types.InlineKeyboardButton(f"{sc.title} - {price} so'm",callback_data=f"product,{sc.id}")
        product.add(item_product)
        global product_sms
        if CartItemTelegram.objects.filter(product=sc,cart=usercart,check=False):
            item_plus = types.InlineKeyboardButton("➕",callback_data=f"plus,{sc.id}")
            item_minus  = types.InlineKeyboardButton("➖",callback_data=f"minus,{sc.id}")
            product.add(item_minus,item_plus)
        else:
            pass
    qaytish = types.InlineKeyboardButton("⬅️Orqaga",callback_data="davay_orqaga")
    if CartItemTelegram.objects.filter(cart=usercart,check=False):
        sotib_olish = types.InlineKeyboardButton("💰Buyurtma berish💰",callback_data="buyurtma")
        product.add(qaytish,sotib_olish)
    else:
        product.add(qaytish)
    return product

def subcategory_handler(message):
    global sub
    sub = message.text
    try:
        sub_cat = Subcategory.objects.get(title=sub)
        telegram_user = UserTelegram.objects.get(telegram_id=message.chat.id)
        usercart, created = CartTelegram.objects.get_or_create(user=telegram_user)
        a = 0
        savat = ""
        price_summary = 0
        if CartItemTelegram.objects.filter(cart=usercart,check=False):
            for pr in CartItemTelegram.objects.filter(cart=usercart,check=False):
                price = pr.product.price if pr.product.sale == False else pr.product.price_in_sale
                dona_yoki_kg = "dona" if pr.product.kg == False else "kg"
                pr.price_ht = pr.quantity * price
                pr.save()
                price_summary += pr.price_ht
                a +=1
                savat+=f"📦№{a} - <b>{pr.product}</b>\n⚖️{price} so'm * {pr.quantity} {dona_yoki_kg} = {price * pr.quantity} so'm\n___________________________________\n\n"
            product_sms = bot.send_message(message.chat.id,f"🛒<b>Sizning savatchangizda:\n\n{savat}💸Jami summa: {price_summary} so'm</b>",reply_markup=knopka(message,sub_cat,usercart)) 
            
        else:
            product_sms = bot.send_message(message.chat.id,"Savatchangiz bo'sh!",reply_markup=knopka(message,sub_cat,usercart))
        bot.register_next_step_handler(product_sms,cart)
    except:
        pass
@bot.callback_query_handler(func=lambda call: True)
def cart(call):
    global sub
    sub_cat = Subcategory.objects.get(title=sub)
    global product
    try:
        if "buyurtma" == call.data:
            location = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
            button = types.KeyboardButton(text="📍Lokatsiyani yuborish📍",request_location=True)
            location.add(button)
            bot.delete_message(call.message.chat.id,call.message.message_id)
            sub_sms = bot.send_message(call.message.chat.id,"Iltimos, quyidagi tugma orqali lokatsiyangizni yuboring!",reply_markup=location)
            bot.register_next_step_handler(sub_sms,location_distance)
    except:
        pass    
    try:
        if "davay_orqaga" == call.data:
            bot.delete_message(call.message.chat.id,call.message.message_id)
            sub_sms = bot.send_message(call.message.chat.id,"Iltimos, quyidagi kategoriyalardan birini tanlang!",reply_markup=category)
            bot.register_next_step_handler(sub_sms,category_handler)
    except:
        pass
    try:
        if "plus" in call.data.split(","):
            product_it = Product.objects.get(id=call.data.split(",")[1])
            telegram_user = UserTelegram.objects.get(telegram_id=call.message.chat.id)
            usercart, created = CartTelegram.objects.get_or_create(user=telegram_user)
            if created == False:
                if CartItemTelegram.objects.filter(product=product_it,cart=usercart):
                    cartitem = CartItemTelegram.objects.get(product=product_it,cart=usercart)
                    cartitem.quantity += 1
                    cartitem.save()
                    bot.answer_callback_query(callback_query_id=call.id, text="Savatchaga qo'shildi✅", show_alert=False)
                    savat = ""
                    a = 0
                    price_summary = 0
                    for pr in CartItemTelegram.objects.filter(cart=usercart,check=False):
                        dona_yoki_kg = "dona" if pr.product.kg == False else "kg"
                        price = pr.product.price if pr.product.sale == False else pr.product.price_in_sale
                        a +=1
                        pr.price_ht = pr.quantity * price
                        pr.save()
                        price_summary += pr.price_ht
                        savat+=f"📦№{a} - <b>{pr.product}</b>\n⚖️{price} so'm * {pr.quantity} {dona_yoki_kg} = {price * pr.quantity} so'm\n___________________________________\n\n"
                    product = types.InlineKeyboardMarkup()
                    bot.edit_message_text(text=f"🛒<b>Sizning savatchangizda:\n\n{savat}💸Jami summa: {price_summary} so'm</b>",chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=knopka(call.message,sub_cat,usercart))
        if "minus" in call.data.split(","):
            product_it = Product.objects.get(id=call.data.split(",")[1])
            telegram_user = UserTelegram.objects.get(telegram_id=call.message.chat.id)
            usercart, created = CartTelegram.objects.get_or_create(user=telegram_user)
            if created == False:
                if CartItemTelegram.objects.filter(product=product_it,cart=usercart):
                    cartitem = CartItemTelegram.objects.get(product=product_it,cart=usercart)
                    if cartitem.quantity == 0:
                        cartitem.delete()
                    else:
                        cartitem.quantity -= 1
                        cartitem.save()
                        bot.answer_callback_query(callback_query_id=call.id, text="Savatchadan olib tashlandi!✅", show_alert=False)
                    savat = ""
                    a = 0
                    price_summary = 0
                    for pr in CartItemTelegram.objects.filter(cart=usercart,check=False):
                        dona_yoki_kg = "dona" if pr.product.kg == False else "kg"
                        price = pr.product.price if pr.product.sale == False else pr.product.price_in_sale
                        a +=1
                        pr.price_ht = pr.quantity * price
                        pr.save()
                        price_summary += pr.price_ht
                        if pr.quantity == 0:
                            pr.delete()
                        else:
                            pass 
                        savat+=f"📦№{a} - <b>{pr.product}</b>\n⚖️{price} so'm * {pr.quantity} {dona_yoki_kg} = {price * pr.quantity} so'm\n___________________________________\n\n"
                    
                    product = types.InlineKeyboardMarkup()
                

                    bot.edit_message_text(text=f"🛒<b>Sizning savatchangizda:\n\n{savat}💸Jami summa: {price_summary} so'm</b>",chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=knopka(call.message,sub_cat,usercart))
    except:
        pass
    try:
        if "product" in call.data.split(","):
            product_it = Product.objects.get(id=call.data.split(",")[1])
            telegram_user = UserTelegram.objects.get(telegram_id=call.message.chat.id)
            usercart, created = CartTelegram.objects.get_or_create(user=telegram_user)
            if CartItemTelegram.objects.filter(product=product_it,cart=usercart,check=False):
                bot.answer_callback_query(callback_query_id=call.id, text="Bu maxsulotdan tanlab bo'ldingiz!😊", show_alert=False)
            else:
                cartitem = CartItemTelegram.objects.create(product=product_it,cart=usercart)
                savat = ""
                a = 0
                price_summary = 0
                for pr in CartItemTelegram.objects.filter(cart=usercart,check=False):
                    dona_yoki_kg = "dona" if pr.product.kg == False else "kg"
                    price = pr.product.price if pr.product.sale == False else pr.product.price_in_sale
                    a +=1
                    pr.price_ht = pr.quantity * price
                    pr.save()
                    price_summary += pr.price_ht
                    savat+=f"📦№{a} - <b>{pr.product}</b>\n⚖️{price} so'm * {pr.quantity} {dona_yoki_kg} = {price * pr.quantity} so'm\n___________________________________\n\n"
                product = types.InlineKeyboardMarkup()
                
                bot.edit_message_text(text=f"🛒<b>Sizning savatchangizda:\n\n{savat}💸Jami summa: {price_summary} so'm</b>",chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=knopka(call.message,sub_cat,usercart)) 
    except:
        pass

def location_distance(message):
    # try:
    user = UserTelegram.objects.get(telegram_id=message.chat.id)
    usertcart = CartTelegram.objects.get(user=user)
    from geopy import distance
    taxi_price = 4000
    user_adress = (message.location.latitude,message.location.longitude)
    bozor = (40.64921244079697, 72.24345985276037)
    taxi_distance = distance.distance(bozor,user_adress).km
    if taxi_distance <= 1.5:
        taxi_distance = "%.2f" % taxi_distance
        taxi_price = 4000
    else:
        taxi_price += (taxi_distance-1.5)*1300
        taxi_price = "%.2f" % taxi_price
        taxi_distance = "%.2f" % taxi_distance 
    order = TelegramOrder()
    order.mahalla = user_adress
    order.phone = user.phone
    order.cart = usertcart
    order.km = float(taxi_distance)
    order.dostavka  = float(taxi_price)
    price_summary = 0
    savat = ""
    a = 0 
    savat2 = ""
    for pr in CartItemTelegram.objects.filter(cart=usertcart,check=False):
        dona_yoki_kg = "dona" if pr.product.kg == False else "kg"
        price = pr.product.price if pr.product.sale == False else pr.product.price_in_sale
        pr.price_ht = pr.quantity * price
        price_summary += pr.price_ht
        a+=1       
        savat+=f"№{a} - {pr.product}\n{price} so'm * {pr.quantity} {dona_yoki_kg} = {price * pr.quantity} so'm\n___________________________________\n\n"
        savat2+=f">>{a} - {pr.product}\n>>{price} so'm * {pr.quantity} {dona_yoki_kg} = {price * pr.quantity} so'm\n___________________________________\n\n"

    order.over_all_products = price_summary
    order.save()
    pdffile  = f"<b>BUYURTMA RAQAMI: {order.id}</b>\n\n<b>Siz xarid qilgan maxsulotlar:\n\n{savat}Jami summa: {price_summary} so'm\n___________________________________\nSizning bozor bilan masofangiz {taxi_distance} km. \nSizga yetkazib berish hizmati {taxi_price} so'mni tashkil etadi!</b>"
    pdffile2  = f"BUYURTMA RAQAMI: {order.id}\n\n>>>>>Siz xarid qilgan maxsulotlar:\n\n{savat2}Jami summa: {price_summary} so'm\n___________________________________\nSizning bozor bilan masofangiz {taxi_distance} km. \nSizga yetkazib berish hizmati {taxi_price} so'mni tashkil etadi!<<<<<"    
    file = open(f"cheklar/{order.id}.txt", "w")
    file.write(pdffile)
    file.close() 
    import qrcode
    img = qrcode.make(pdffile2)
    img.save(f"qr/{order.id}.png")
    f = open(f"qr/{order.id}.png", "rb")

    # for pr in CartItemTelegram.objects.filter(cart=usertcart,check=False):
    #     pr.check= True
    #     pr.save()
    
    bot.send_photo(message.chat.id,photo=f,caption=pdffile)
    # except:
    #     pass


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        bot.polling(none_stop=True,skip_pending=True)
    

