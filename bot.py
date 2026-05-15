import telebot
from telebot import types
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# التوكن الجديد والمظبوط بتاعك
API_TOKEN = '8941642774:AAEbqbBDiKi2SowXfR1Thnf6YuI3wAs4phU'
bot = telebot.TeleBot(API_TOKEN)

# تحميل النموذج الشامل لـ 200 لغة أوفلاين (للأبد بعد أول تحميل)
print("جاري تحميل محرك الـ 200 لغة الأوفلاين...")
model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
print("المحرك جاهز تمامًا لخدمتك لقرنين بدون إنترنت!")

# قاموس لتخزين اللغة المستهدفة لكل مستخدم
user_target_lang = {}

# قائمة اللغات بالأزرار مع التعديل اللي طلبته (والنموذج يدعم 200 لغة في الخلفية)
LANGUAGES_20 = {
    "العربية 🇪🇬": "arb_Arab", " can الإنجليزية 🇺🇸": "eng_Latn", "الفرنسية 🇫🇷": "fra_Latn",
    "الألمانية 🇩🇪": "deu_Latn", "الإسبانية 🇪🇸": "spa_Latn", "الروسية 🇷🇺": "rus_Cyrl",
    "التركية 🇹🇷": "tur_Latn", "الإيطالية 🇮🇹": "ita_Latn", "الصينية 🇨🇳": "zho_Hans",
    "اليابانية 🇯🇵": "jpn_Jpan", "الكورية 🇰🇷": "kor_Hani", "الهندية 🇮🇳": "hin_Deva",
    "البرتغالية 🇵🇹": "por_Latn", "الهولندية 🇳🇱": "nld_Latn", "الفارسية 🇮🇷": "pes_Aran",
    "الأوردو 🇵🇰": "urd_Arab", "🇮🇩 الإندونيسية": "ind_Latn", "السويدية 🇸🇪": "swe_Latn",
    "اليونانية 🇬رك": "ell_Grek", "أخرائيل 🤮": "heb_Hebr"
}

# دالة لإنشاء لوحة الأزرار
def get_lang_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for lang_name, lang_code in LANGUAGES_20.items():
        buttons.append(types.InlineKeyboardButton(text=lang_name, callback_data=f"set_{lang_code}_{lang_name}"))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "مرحبًا بك في بوت الترجمة الأوفلاين الخارق (200+ لغة) 🚀\n\n"
        "الرجاء اختيار لغة الترجمة من الأزرار بالأسفل، ثم أرسل النص ليتم ترجمته فورًا بدون إنترنت لقرنين قادمين!", 
        reply_markup=get_lang_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def handle_lang_selection(call):
    data_parts = call.data.split("_")
    lang_code = f"{data_parts[1]}_{data_parts[2]}"
    lang_name = data_parts[3]
    
    user_target_lang[call.message.chat.id] = lang_code
    
    bot.answer_callback_query(call.id, f"تم اختيار {lang_name}")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🎯 تم ضبط اللغة النشطة: **{lang_name}**\n\nأرسل أي نص الآن وسيتم ترجمته فورًا أوفلاين. يمكنك تغيير اللغة في أي وقت بإرسال /start.",
        reply_markup=get_lang_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_translation(message):
    chat_id = message.chat.id
    target_code = user_target_lang.get(chat_id, "arb_Arab")
    
    bot.reply_to(message, "جاري معالجة النص والترجمة أوفلاين... ⏳")
    try:
        translator = pipeline('translation', model=model, tokenizer=tokenizer, tgt_lang=target_code, max_length=512)
        translated_text = translator(message.text)[0]['translation_text']
        
        bot.reply_to(message, f"🎯 الترجمة المعتمدة أوفلاين:\n\n{translated_text}")
    except Exception as e:
        bot.reply_to(message, f"عذرًا، حدث خطأ في المعالجة الداخلية: {e}")

bot.infinity_polling()
