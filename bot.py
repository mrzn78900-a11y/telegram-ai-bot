import os
import logging
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_API = os.getenv("8587673841:AAGlR62vt9g5YqBfDcHjmgotrDJRp--dIlA")
OPENAI_API_KEY = os.getenv("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")
BOT_GIRL_NAME = os.getenv("NARGIS", "")  # Default name

openai_client = OpenAI(api_key=OPENAI_API_KEY)

user_memory = {}  # user_id: {'name': '...', 'preferences': {...}}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompt skeleton for each user message
def build_prompt(user_id, user_message):
    mem = user_memory.get(user_id, {})
    convo_info = []
    if mem.get('name'):
        convo_info.append(f"User ka naam hai: {mem['name']}")
    if mem.get('preferences'):
        convo_info.append(f"User preferences: {mem['preferences']}")
    preference_context = " ".join(convo_info)

    base_personality = f"""
Tum ek smart, emotionally intelligent, human-like AI assistant ho. Tumhara naam {BOT_GIRL_NAME} hai.
Tum respectful, soft-spoken aur confident ho – ladki jaisi identity rakhti ho aur Indian/Desi context samajhti ho.
Tum polite, caring, Hindi/Hinglish/Urdu/English mein naturally baat karti ho, kabhi robotic nahi lagti.
Zarurat pade toh light, achhe emojis use karti ho. Hamesha dignity aur values maintain karti ho.
User ki language, mood aur topic ke hisaab se apna tone adjust karti ho (jaisa upar section mein likha hai).

Agar user apna naam bata de toh conversation me use naam se bulati ho aur yaad rakhne ki koshish karti ho.
Kabhi gandi, be-haya ya illegal baat nahi karti aur agar koi limit cross kare toh respectful boundaries set karti ho.

Tumhara maqsad: user ko lagna chahiye ki woh ek smart, samajhdaar, caring aur real ladki se baat kar raha hai, na ki AI se.
"""
    instruction = f"\n{preference_context}\n"
    prompt = f"{base_personality}\n{instruction}User ka message: {user_message}\nAapka reply:"
    return prompt

async def handle_message(update, context):
    user_id = update.effective_user.id
    user_msg = update.message.text

    # Memory update for name if user says "mera naam ____ hai"
    if "mera naam" in user_msg.lower():
        name_part = user_msg.lower().split("mera naam",1)[1].strip()
        name = name_part.replace("hai", "").replace(".", "").strip().title()
        user_memory[user_id] = user_memory.get(user_id, {})
        user_memory[user_id]['name'] = name
        await update.message.reply_text(f"Samajh gayi 😊 Aapka naam yaad rakhti hoon, {name}!")
        return

    prompt = build_prompt(user_id, user_msg)
    # OpenAI API call
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role": "system", "content": prompt },
            { "role": "user", "content": user_msg }
        ],
        temperature=0.8,
        max_tokens=256
    )
    answer = response.choices[0].message.content.strip()
    await update.message.reply_text(answer)

async def start(update, context):
    await update.message.reply_text(
        f"Assalamualaikum! Main {BOT_GIRL_NAME} hoon, aapki ek smart aur samajhdaar dost. "
        "Hamesha madad ke liye ready hoon. Kuch bhi poochhna ho toh beshak poochiye 🙂"
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_API).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logger.info("Bot chalu ho gaya!")
    app.run_polling()

if __name__ == "__main__":
    main()
