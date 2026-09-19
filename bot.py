import os
import telebot

# توکن ربات
TOKEN = "8444346591:AAGcEczd2ttxZmnq3mlVoQpE3iIc27pQces"

# آیدی عددی تلگرام خودت به عنوان ادمین
ADMIN_CHAT_ID = 344610588

# آیدی کانال شما (ثابت شده)
CHANNEL_USERNAME = "@region_12pr"

bot = telebot.TeleBot(TOKEN)

# حافظه موقت برای ذخیره مراحل و اطلاعات کاربران
user_data = {}


# تابع بررسی عضویت کاربر در کانال
def check_membership(user_id):
  try:
    member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if member.status in ["member", "administrator", "creator"]:
      return True
    else:
      return False
  except Exception:
    return False


@bot.message_handler(commands=["start"])
def send_welcome(message):
  chat_id = message.chat.id
  user_id = message.from_user.id

  # بررسی عضویت اجباری در کانال
  if not check_membership(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(
            "📢 عضویت در کانال منطقه",
            url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}",
        )
    )
    markup.row(
        telebot.types.InlineKeyboardButton(
            "🔄 بررسی مجدد عضویت", callback_data="check_join"
        )
    )

    bot.send_message(
        chat_id,
        "❌ برای استفاده از امکانات ربات، لطفاً ابتدا در کانال رسمی ما"
        f" ({CHANNEL_USERNAME}) عضو شوید و سپس روی دکمه بررسی مجدد کلیک کنید.",
        reply_markup=markup,
    )
    return

  # ذخیره خودکار آیدی کاربر در فایل برای ارسال همگانی
  try:
    with open("users.txt", "r") as f:
      users = f.read().splitlines()
    if str(chat_id) not in users:
      with open("users.txt", "a") as f:
        f.write(str(chat_id) + "\n")
  except FileNotFoundError:
    with open("users.txt", "w") as f:
      f.write(str(chat_id) + "\n")

  markup = telebot.types.InlineKeyboardMarkup()
  markup.row(
      telebot.types.InlineKeyboardButton(
          "🧭 گردشگری منطقه", callback_data="tourism"
      ),
      telebot.types.InlineKeyboardButton(
          "👥 ملاقات مردمی (ثبت فرم)", callback_data="meetings"
      ),
  )
  markup.row(
      telebot.types.InlineKeyboardButton(
          "🌟 خبر ویژه", callback_data="special_news"
      ),
      telebot.types.InlineKeyboardButton("📝 ثبت درخواست", callback_data="requests"),
  )
  markup.row(
      telebot.types.InlineKeyboardButton(
          "📸 شهروند خبرنگار", callback_data="citizen_reporter"
      ),
      telebot.types.InlineKeyboardButton(
          "🚇 نقشه مترو منطقه ۱۲", callback_data="metro_brt"
      ),
  )
  markup.row(
      telebot.types.InlineKeyboardButton(
          "📍 اماکن و مراکز", callback_data="locations"
      ),
      telebot.types.InlineKeyboardButton("ℹ️ درباره منطقه", callback_data="about"),
  )
  markup.row(
      telebot.types.InlineKeyboardButton("☎️ تماس با ما", callback_data="contact")
  )

  bot.send_message(
      chat_id,
      f"سلام {message.from_user.first_name} عزیز!\nبه ربات خدمات الکترونیک"
      " **شهرداری منطقه ۱۲** خوش آمدید.\n\nلطفاً از منوی زیر گزینه مورد نظر"
      " خود را انتخاب کنید:",
      reply_markup=markup,
      parse_mode="Markdown",
  )


# دستور ارسال همگانی برای ادمین (/sendall)
@bot.message_handler(commands=["sendall"])
def broadcast_message(message):
  chat_id = message.chat.id

  if chat_id != ADMIN_CHAT_ID:
    bot.send_message(chat_id, "❌ شما اجازه دسترسی به این دستور را ندارید.")
    return

  text_to_send = message.text.replace("/sendall", "").strip()

  if not text_to_send:
    bot.send_message(
        chat_id,
        "⚠️ لطفاً متن پیام خود را بعد از دستور بنویسید.\nمثال:\n/sendall سلام این"
        " یک پیام همگانی است",
    )
    return

  try:
    with open("users.txt", "r") as f:
      users = f.read().splitlines()
  except FileNotFoundError:
    bot.send_message(chat_id, "❌ هیچ کاربری هنوز در ربات ثبت‌نام نکرده است.")
    return

  success_count = 0
  fail_count = 0

  for user_id in users:
    try:
      bot.send_message(int(user_id), text_to_send)
      success_count += 1
    except Exception:
      fail_count += 1

  bot.send_message(
      chat_id,
      "✅ پیام همگانی با موفقیت ارسال شد!\n\n"
      f"📤 ارسال شده به: {success_count} کاربر\n"
      f"❌ ناموفق: {fail_count} کاربر",
  )


# مدیریت کلیک روی دکمه‌ها
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  chat_id = call.message.chat.id
  user_id = call.from_user.id

  if call.data == "check_join":
    if check_membership(user_id):
      bot.answer_callback_query(call.id, "✅ عضویت شما تایید شد!")
      send_welcome(call.message)
    else:
      bot.answer_callback_query(
          call.id,
          "❌ شما هنوز در کانال عضو نشده‌اید!",
          show_alert=True,
      )
    return

  if not check_membership(user_id):
    bot.answer_callback_query(
        call.id,
        "❌ لطفاً ابتدا در کانال عضو شوید و روی بررسی مجدد کلیک کنید.",
        show_alert=True,
    )
    return

  if call.data == "special_news":
    bot.answer_callback_query(call.id)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(
            "🌟 ورود به بخش خبر ویژه شهرداری منطقه ۱۲",
            url="https://region12.tehran.ir/",
        )
    )
    bot.send_message(
        chat_id,
        "🌟 **آخرین اخبار و اطلاعیه‌های ویژه منطقه ۱۲:**\n\nبرای مشاهده"
        " مشروح اخبار و رویدادهای ویژه، روی دکمه زیر کلیک کنید:",
        reply_markup=markup,
        parse_mode="Markdown",
    )

  elif call.data == "meetings":
    user_data[chat_id] = {"step": "waiting_for_national_code"}
    bot.answer_callback_query(call.id)
    bot.send_message(
        chat_id,
        "📋 **فرم ثبت‌نام ملاقات مردمی**\n\nلطفاً **کد ملی** خود را وارد کنید:",
        parse_mode="Markdown",
    )
  elif call.data == "citizen_reporter":
    bot.answer_callback_query(call.id)
    reporter_file = "reporters.txt"
    registered = False
    user_level = 1
    user_name = ""

    if os.path.exists(reporter_file):
      with open(reporter_file, "r", encoding="utf-8") as f:
        for line in f:
          parts = line.strip().split("|")
          if len(parts) >= 5 and parts[0] == str(chat_id):
            registered = True
            user_level = int(parts[4])
            user_name = parts[2]
            break

    if not registered:
      user_data[chat_id] = {"step": "reporter_national_code"}
      bot.send_message(
          chat_id,
          "📸 **ثبت‌نام در پویش شهروند خبرنگار**\n\nلطفاً **کد ملی** خود را وارد"
          " کنید:",
          parse_mode="Markdown",
      )
    else:
      markup = telebot.types.InlineKeyboardMarkup()
      markup.row(
          telebot.types.InlineKeyboardButton(
              "📤 ارسال خبر یا گزارش جدید", callback_data="send_news_item"
          )
      )
      markup.row(
          telebot.types.InlineKeyboardButton(
              "🏆 مشاهده ۵ نفر برتر (رتبه‌بندی)",
              callback_data="show_top_reporters",
          )
      )
      bot.send_message(
          chat_id,
          f"🌟 کاربر گرامی ({user_name})، شما در سامانه شهروند خبرنگار ثبت‌نام"
          f" کرده‌اید.\n📊 **سطح فعلی شما:** سطح {user_level}\n\nلطفاً یکی از"
          " گزینه‌های زیر را انتخاب کنید:",
          reply_markup=markup,
          parse_mode="Markdown",
      )

  elif call.data == "send_news_item":
    bot.answer_callback_query(call.id)
    user_data[chat_id] = {"step": "waiting_for_news_content"}
    bot.send_message(
        chat_id,
        "✍️ لطفاً **متن خبر، عکس یا گزارش** خود را ارسال کنید (می‌توانید توضیحات"
        " و تصویر را با هم بفرستید):",
        parse_mode="Markdown",
    )

  elif call.data == "show_top_reporters":
    bot.answer_callback_query(call.id)
    reporter_file = "reporters.txt"
    reporters_list = []

    if os.path.exists(reporter_file):
      with open(reporter_file, "r", encoding="utf-8") as f:
        for line in f:
          parts = line.strip().split("|")
          if len(parts) >= 5:
            reporters_list.append({"name": parts[2], "level": int(parts[4])})

    reporters_list.sort(key=lambda x: x["level"], reverse=True)
    top_5 = reporters_list[:5]

    text = "🏆 **لیست ۵ نفر برتر پویش شهروند خبرنگار:**\n\n"
    if not top_5:
      text += "هنوز کاربری در سامانه ثبت‌نام نکرده است."
    else:
      medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
      for i, rep in enumerate(top_5):
        text += (
            f"{medals[i]} **{rep['name']}** — 📊 سطح (Level):"
            f" `{rep['level']}`\n"
        )

    text += (
        "\n🎁 در پایان هر ماه به نفرات برتر جوایز ارزنده‌ای اهطا خواهد شد!"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown")

  elif call.data.startswith("approve_reporter_"):
    target_chat_id = call.data.replace("approve_reporter_", "")
    reporter_file = "reporters.txt"
    updated_lines = []
    found = False
    new_lvl = 1

    if os.path.exists(reporter_file):
      with open(reporter_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
      for line in lines:
        parts = line.strip().split("|")
        if len(parts) >= 5 and parts[0] == target_chat_id:
          found = True
          new_lvl = int(parts[4]) + 1
          updated_line = (
              f"{parts[0]}|{parts[1]}|{parts[2]}|{parts[3]}|{new_lvl}\n"
          )
          updated_lines.append(updated_line)
        else:
          updated_lines.append(line)

      if found:
        with open(reporter_file, "w", encoding="utf-8") as f:
          f.writelines(updated_lines)

        bot.answer_callback_query(
            call.id,
            f"✅ خبر تایید شد و لول کاربر به {new_lvl} ارتقا یافت!",
            show_alert=True,
        )
        try:
          bot.send_message(
              int(target_chat_id),
              "🎉 **خبر شما تایید شد!**\n\nتبریک می‌گویم؛ به دلیل ارسال گزارش"
              f" ارزشمندتان، سطح (Level) شما به **سطح {new_lvl}** ارتقا"
              " یافت. 🚀",
              parse_mode="Markdown",
          )
        except Exception:
          pass
      else:
        bot.answer_callback_query(
            call.id, "❌ کاربر در سیستم پیدا نشد!", show_alert=True
        )

  elif call.data.startswith("reject_reporter_"):
    target_chat_id = call.data.replace("reject_reporter_", "")
    bot.answer_callback_query(
        call.id, "❌ خبر رد شد و به کاربر اطلاع داده شد.", show_alert=True
    )
    try:
      bot.send_message(
          int(target_chat_id),
          "⚠️ **گزارش ارسالی شما بررسی شد.**\n\nمتأسفانه خبر یا گزارش شما شرایط"
          " لازم برای تایید در پویش شهروند خبرنگار را نداشت. از تلاش شما"
          " سپاسگزاریم. 🙏",
          parse_mode="Markdown",
      )
    except Exception:
      pass

  elif call.data == "tourism":
    bot.answer_callback_query(call.id)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(
            "🌐 ورود به وب‌سایت گردشگری منطقه ۱۲",
            url=(
                "https://region12.tehran.ir/%D8%B5%D9%81%D8%AD%D8%A7%D8%AA"
                "-%D9%82%D8%AF%DB%8C%D9%85%DB%8C/%D9%85%D8%B9%D8%B1%D9%81%DB%8C"
                "-%D9%85%D9%86%D8%B7%D9%82%D9%87-%DB%81-%DB%82/%DA%AF%D8%B1"
                "-%D8%AF%D8%B4%DA%AF%D8%B1%DB%8ی"
            ),
        )
    )
    bot.send_message(
        chat_id,
        "🧭 **راهنمای گردشگری و جاذبه‌های تاریخی منطقه ۱۲:**\n\nبرای مشاهده"
        " کامل جاذبه‌ها، اماکن تاریخی و اطلاعات گردشگری، روی دکمه زیر کلیک"
        " کنید:",
        reply_markup=markup,
        parse_mode="Markdown",
    )

  elif call.data == "metro_brt":
    bot.answer_callback_query(call.id)

    possible_names = ["metro_map.jpg", "metro_map.png", "metro_map.jpeg"]
    found_photo = None
    for name in possible_names:
      if os.path.exists(name):
        found_photo = name
        break

    if found_photo:
      caption_text = (
          "🚇 **نقشه رسمی و راهنمای مترو منطقه ۱۲:**\n\nمی‌توانید نقشه کامل"
          " ایستگاه‌ها و خطوط مترو را در تصویر زیر مشاهده کنید."
      )
      try:
        with open(found_photo, "rb") as photo_file:
          bot.send_photo(
              chat_id,
              photo_file,
              caption=caption_text,
              parse_mode="Markdown",
          )
      except Exception as e:
        bot.send_message(chat_id, f"❌ خطا در ارسال عکس: {e}")
    else:
      bot.send_message(
          chat_id,
          "❌ فایل عکس نقشه پیدا نشد! لطفاً بررسی کنید که عکس با نام"
          " `metro_map.jpg` دقیقاً در همان پوشه فایل `bot.py` قرار داشته باشد.",
      )
  else:
    responses = {
        "requests": "📝 سامانه ثبت درخواست‌ها و شکایات مردمی:",
        "locations": "📍 اماکن و مراکز مهم، سرای محلات و ادارات:",
        "contact": (
            "☎️ **دفترچه تلفن و راه‌های ارتباطی شهرداری منطقه ۱۲:**\n\n"
            "🏛️ **تلفن گویا:** `96028000` (داخلی: `28000`)\n"
            "📞 **مرکز تماس:** `96028888` (داخلی: `28888`)\n\n"
            "───────────────────\n"
            "🏢 **معاونت‌ها و ادارات:**\n\n"
            "📐 **شهرسازی و معماری:**\n"
            "• دفتر معاونت: `96028200` (داخلی: `28200`)\n\n"
            "🏗️ **فنی و عمران:**\n"
            "• دفتر معاونت: `96028300` (داخلی: `28300`)\n\n"
            "🚦 **حمل و نقل و ترافیک:**\n"
            "• دفتر معاونت: `96028400` (داخلی: `28400`)\n\n"
            "🌳 **خدمات شهری و محیط زیست:**\n"
            "• دفتر معاونت: `96028500` (داخلی: `28500`)\n\n"
            "📊 **برنامه‌ریزی و توسعه شهری:**\n"
            "• دفتر معاونت: `96028600` (داخلی: `28600`)\n\n"
            "🎭 **اجتماعی و فرهنگی:**\n"
            "• دفتر معاونت: `96028700` (داخلی: `28700`)\n\n"
            "💰 **مالی و اقتصاد شهری:**\n"
            "• دفتر معاونت: `96028900` (داخلی: `28900`)\n\n"
            "───────────────────\n"
            "🏙️ **ناحیه‌های شهرداری:**\n"
            "• ناحیه ۱: `96028150` (داخلی: `28150`)\n"
            "• ناحیه ۲: `96028250` (داخلی: `28250`)\n"
            "• ناحیه ۳: `96028350` (داخلی: `28350`)\n"
            "• ناحیه ۴: `96028450` (داخلی: `28450`)\n"
            "• ناحیه ۵: `96028550` (داخلی: `28550`)\n"
            "• ناحیه ۶: `96028650` (داخلی: `28650`)\n\n"
            "───────────────────\n"
            "📸 **اداره گردشگری:**\n"
            "• دفتر گردشگری: `96028774` (داخلی: `28774`)\n"
            "• مدیر گردشگری: `96028770` (داخلی: `28770`)\n"
            "• کارشناس گردشگری: `96028772` (داخلی: `28772`)"
        ),
        "about": (
            "ℹ️ **درباره منطقه ۱۲ شهرداری تهران:**\n\n"
            "منطقه ۱۲ شهرداری تهران، از مناطق قدیمی شهری در مرکز تهران است به گونه"
            " ای که مرز بین مرکز و شرق تهران به حساب می‌آید. از شمال به خیابان"
            " انقلاب، از غرب به خیابان حافظ و خیابان وحدت اسلامی و از جنوب به"
            " خیابان شوش و از شرق به خیابان ۱۷ شهریور و اتوبان شهید محلاتی محدود"
            " می‌شود.\n\n"
            "منطقه دوازده از شمال با مناطق هفت و شش، از شرق با مناطق سیزده و"
            " چهارده، از جنوب با مناطق پانزده و شانزده و از غرب با منطقه یازده"
            " همجوار است.\n\n"
            "در منطقه ۱۲ تهران بناهای تاریخی بسیاری از دوران قاجار و پهلوی اول به"
            " جای مانده است. همچنین وجود مراکز سیاسی همچون ساختمان مجلس شورای"
            " اسلامی، وزارتخانه‌ها، دادگستری استان تهران، سفارتخانه‌های برخی از"
            " کشورها مانند روسیه و آلمان، موقعیت ویژه ای را در این منطقه بوجود"
            " آورده است."
        ),
    }
    text = responses.get(call.data, "گزینه نامعتبر است.")
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, text, parse_mode="Markdown")


# مدیریت مرحله‌به‌مرحله پیام‌های متنی کاربران
@bot.message_handler(
    func=lambda message: True, content_types=["text", "photo", "video", "document"]
)
def handle_text_messages(message):
  chat_id = message.chat.id
  user_id = message.from_user.id

  if not check_membership(user_id):
    bot.send_message(
        chat_id,
        "❌ برای استفاده از ربات، لطفاً ابتدا دستور /start را بزنید و در کانال"
        " عضو شوید.",
    )
    return

  if chat_id in user_data:
    current_step = user_data[chat_id].get("step")

    # مراحل ثبت‌نام ملاقات مردمی
    if current_step == "waiting_for_national_code":
      user_data[chat_id]["national_code"] = message.text
      user_data[chat_id]["step"] = "waiting_for_fullname"
      bot.send_message(
          chat_id,
          "👤 لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
          parse_mode="Markdown",
      )

    elif current_step == "waiting_for_fullname":
      user_data[chat_id]["fullname"] = message.text
      user_data[chat_id]["step"] = "waiting_for_problem"
      bot.send_message(
          chat_id,
          "✍️ لطفاً **موضوع و شرح مشکل** خود را مطرح کنید:",
          parse_mode="Markdown",
      )

    elif current_step == "waiting_for_problem":
      user_data[chat_id]["problem"] = message.text
      user_data[chat_id]["step"] = "waiting_for_phone"
      bot.send_message(
          chat_id,
          "📞 لطفاً **شماره تماس** خود را وارد کنید:",
          parse_mode="Markdown",
      )

    elif current_step == "waiting_for_phone":
      user_data[chat_id]["phone"] = message.text

      n_code = user_data[chat_id]["national_code"]
      fname = user_data[chat_id]["fullname"]
      problem = user_data[chat_id]["problem"]
      phone = user_data[chat_id]["phone"]

      bot.send_message(
          chat_id,
          "✅ اطلاعات شما با موفقیت ثبت شد و برای بررسی نهایی ارسال گردید.\n\n"
          f"🆔 کد ملی: {n_code}\n"
          f"👤 نام و نام خانوادگی: {fname}\n"
          f"📝 مشکل: {problem}\n"
          f"📞 شماره تماس: {phone}",
      )

      admin_report = (
          "🚨 *فرم جدید ملاقات مردمی ثبت شد!*\n\n"
          f"👤 نام و نام خانوادگی: {fname}\n"
          f"🆔 کد ملی: {n_code}\n"
          f"📞 شماره تماس: {phone}\n"
          f"📝 شرح مشکل: {problem}\n"
          f"🌐 آیدی کاربر: @{message.from_user.username or 'ندارد'}"
      )

      try:
        bot.send_message(ADMIN_CHAT_ID, admin_report, parse_mode="Markdown")
      except Exception as e:
        print(f"خطا در ارسال پیام به ادمین: {e}")

      del user_data[chat_id]

    # مراحل ثبت‌نام شهروند خبرنگار
    elif current_step == "reporter_national_code":
      user_data[chat_id]["rep_national_code"] = message.text
      user_data[chat_id]["step"] = "reporter_fullname"
      bot.send_message(
          chat_id,
          "👤 لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
          parse_mode="Markdown",
      )

    elif current_step == "reporter_fullname":
      user_data[chat_id]["rep_fullname"] = message.text
      user_data[chat_id]["step"] = "reporter_phone"
      bot.send_message(
          chat_id,
          "📞 لطفاً **شماره تماس** خود را وارد کنید:",
          parse_mode="Markdown",
      )

    elif current_step == "reporter_phone":
      phone = message.text
      n_code = user_data[chat_id]["rep_national_code"]
      fname = user_data[chat_id]["rep_fullname"]

      with open("reporters.txt", "a", encoding="utf-8") as f:
        f.write(f"{chat_id}|{n_code}|{fname}|{phone}|1\n")

      del user_data[chat_id]

      bot.send_message(
          chat_id,
          "🎉 **ثبت‌نام شما با موفقیت انجام شد!**\n\n"
          "شما اکنون در پویش **شهروند خبرنگار** ثبت‌نام کردید و سطح شما"
          " **سطح ۱** است. 🚀\n\nمی‌توانید از منوی شهروند خبرنگار، اخبار و"
          " گزارش‌های خود را برای ما ارسال کنید تا با تایید شما، لول‌تان افزایش"
          " پیدا کند!",
          parse_mode="Markdown",
      )

    # مرحله ارسال خبر توسط شهروند خبرنگار
    elif current_step == "waiting_for_news_content":
      del user_data[chat_id]

      reporter_name = "ناشناس"
      if os.path.exists("reporters.txt"):
        with open("reporters.txt", "r", encoding="utf-8") as f:
          for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 5 and parts[0] == str(chat_id):
              reporter_name = parts[2]
              break

      bot.send_message(
          chat_id,
          "✅ خبر یا گزارش شما با موفقیت دریافت شد و برای بررسی و تایید به"
          " ادمین ارسال گردید. با تشکر از مشارکت شما! 🙏",
      )

      # دکمه‌های تایید و رد برای ادمین
      markup = telebot.types.InlineKeyboardMarkup()
      markup.row(
          telebot.types.InlineKeyboardButton(
              "✅ تایید و افزایش سطح (لول)",
              callback_data=f"approve_reporter_{chat_id}",
          ),
          telebot.types.InlineKeyboardButton(
              "❌ رد کردن خبر", callback_data=f"reject_reporter_{chat_id}"
          ),
      )

      admin_msg = (
          f"📰 **گزارش جدید شهروند خبرنگار:**\n\n"
          f"👤 فرستنده: {reporter_name}\n"
          f"🌐 آیدی چت کاربر: `{chat_id}`"
      )

      try:
        bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
        bot.forward_message(ADMIN_CHAT_ID, chat_id, message.message_id)
        bot.send_message(
            ADMIN_CHAT_ID,
            "👆 برای تایید یا رد این خبر، از دکمه‌های زیر استفاده کنید:",
            reply_markup=markup,
        )
      except Exception as e:
        print(f"خطا در ارسال خبر به ادمین: {e}")

  else:
    bot.send_message(
        chat_id,
        "لطفاً از دکمه‌های منو استفاده کنید یا برای شروع دستور /start را بزنید.",
    )


print("Bot is running...")
bot.infinity_polling()