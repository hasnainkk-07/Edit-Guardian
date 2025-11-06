import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from pymongo import MongoClient
from Anonymous import application
from Anonymous.config import Config as c, Config


# MongoDB connection
client = MongoClient(c.MONGO_URI)
db = client["word_mine_bot"]
scores_collection = db["scores"]
chats_collection = db["chats"]

# File paths
WORDS_FILE = "words.txt"

# Load words from file
def load_words():
    if not os.path.exists(WORDS_FILE):
        raise FileNotFoundError(f"{WORDS_FILE} not found. Please provide a word list.")
    with open(WORDS_FILE, "r") as file:
        return [word.strip().lower() for word in file.readlines()]

# Save words to file
def save_words(words):
    with open(WORDS_FILE, "w") as file:
        file.write("\n".join(words))

# Load or initialize scores
def load_scores():
    scores = {}
    for doc in scores_collection.find():
        scores[doc["user_id"]] = doc["score"]
    return scores

# Save scores to MongoDB
def save_scores(user_id, score):
    scores_collection.update_one(
        {"user_id": user_id},
        {"$set": {"score": score}},
        upsert=True
    )

# Generate feedback (🟥, 🟨, 🟩)
def generate_feedback(guess, target):
    feedback = []
    target_letters = list(target)
    guess_letters = list(guess)

    # First, mark all correct letters (🟩)
    for i in range(len(guess_letters)):
        if guess_letters[i] == target_letters[i]:
            feedback.append("🟩")
            target_letters[i] = None  # Mark as used
            guess_letters[i] = None  # Mark as used
        else:
            feedback.append(None)  # Placeholder for now

    # Then, mark letters that are in the word but in the wrong position (🟨)
    for i in range(len(guess_letters)):
        if guess_letters[i] is not None and guess_letters[i] in target_letters:
            feedback[i] = "🟨"
            target_letters[target_letters.index(guess_letters[i])] = None  # Mark as used
        elif feedback[i] is None:
            feedback[i] = "🟥"  # Letter not in the word

    return " ".join(feedback)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Welcome to Toji • Fushiguro! 🎮\n"
        "Use /new to start a new word guessing game.\n"
        "Use /help to see all commands."
    )

# Command: /new
async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "target_word" in context.chat_data:  # Check if a game is already active in this chat
        await update.message.reply_text(
            "A game is already active in this chat! "
            "Finish it or use /end to end the current game."
        )
        return

    keyboard = [
        [InlineKeyboardButton("3 Letters", callback_data="3")],
        [InlineKeyboardButton("4 Letters", callback_data="4")],
        [InlineKeyboardButton("5 Letters", callback_data="5")],
        [InlineKeyboardButton("6 Letters", callback_data="6")],
        [InlineKeyboardButton("7 Letters", callback_data="7")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a word length to start the game:", reply_markup=reply_markup)

# Handle word length selection
async def select_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    word_length = int(query.data)
    words = load_words()
    target_word = random.choice([word for word in words if len(word) == word_length])
    context.chat_data["target_word"] = target_word  # Store target word in chat_data
    context.chat_data["attempts"] = 0
    context.chat_data["guess_history"] = []  # Initialize guess history
    await query.edit_message_text(f"Game started! Guess a {word_length}-letter word.")

# Handle word guesses
async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if a game is active in this chat
    if "target_word" not in context.chat_data:
        return  # Do nothing if no game is active

    target_word = context.chat_data["target_word"]
    guess = update.message.text.strip().lower()

    # Check if the guess has the correct length
    if len(guess) != len(target_word):
        return  # Ignore guesses with incorrect length

    # Update game data
    context.chat_data["attempts"] += 1
    feedback = generate_feedback(guess, target_word)

    # Add guess and feedback to history
    if "guess_history" not in context.chat_data:
        context.chat_data["guess_history"] = []
    context.chat_data["guess_history"].append(f"{feedback} → {guess.upper()}")

    # Display all guesses in one message
    guess_history_text = "\n".join(context.chat_data["guess_history"])
    await update.message.reply_text(f"{guess_history_text}")

    # Check if the guess is correct
    if guess == target_word:
        # Update scores
        user_id = update.message.from_user.id
        scores = load_scores()
        user_score = scores.get(user_id, 0) + 1
        save_scores(user_id, user_score)

        # Calculate global rank
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        global_rank = next((i + 1 for i, (uid, _) in enumerate(sorted_scores) if uid == user_id), 1)

        # Send win message
        await update.message.reply_text(
            f"🎉 Congratulations {update.message.from_user.first_name}! 🎉\n"
            f"You guessed the word {target_word} correctly!\n"
            f"🏆 You earned 1 point!\n"
            f"📊 Your total score: {user_score}\n"
            f"🌍 Your global rank: {global_rank}"
        )
        context.chat_data.clear()  # Clear game data after winning

# Command: /addword <word>
async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    allowed_user_ids = [6346273488, 8171988347]  # Admin user IDs

    if user_id not in allowed_user_ids:  # Check if user is admin
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /addword <word>")
        return

    word = context.args[0].strip().lower()
    words = load_words()
    if word in words:
        await update.message.reply_text(f"The word '{word}' is already in the list.")
    else:
        words.append(word)
        save_words(words)
        await update.message.reply_text(f"The word '{word}' has been added to the list.")

# Command: /delword <word>
async def del_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    allowed_user_ids = [6346273488, 8171988347]  # Admin user IDs

    if user_id not in allowed_user_ids:  # Check if user is admin
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /delword <word>")
        return

    word = context.args[0].strip().lower()
    words = load_words()
    if word not in words:
        await update.message.reply_text(f"The word '{word}' is not in the list.")
    else:
        words.remove(word)
        save_words(words)
        await update.message.reply_text(f"The word '{word}' has been removed from the list.")

# Command: /checkword <word>
async def check_word_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /checkword <word>")
        return

    word = context.args[0].strip().lower()
    words = load_words()
    if word in words:
        await update.message.reply_text(f"The word '{word}' exists in the bot's word list.")
    else:
        await update.message.reply_text(f"The word '{word}' does NOT exist in the bot's word list.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("No scores yet. Play a game to earn points!")
        return

    # Sort scores in descending order
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Create leaderboard text
    leaderboard_text = "🏆 Global Leaderboard 🏆\n"
    for i, (user_id, score) in enumerate(sorted_scores[:10]):  # Top 10 users
        try:
            user = await context.bot.get_chat(user_id)
            leaderboard_text += f"{i + 1}. {user.first_name}: {score} points\n"
        except:
            leaderboard_text += f"{i + 1}. User {user_id}: {score} points\n"

    await update.message.reply_text(leaderboard_text)

# Command: /check
async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    allowed_user_ids = [6346273488, 8171988347]  # Admin user IDs

    if user_id not in allowed_user_ids:  # Check if user is admin
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Check if a game is active in this chat
    if "target_word" not in context.chat_data:
        await update.message.reply_text("No active game in this chat. Start a new game with /new.")
        return

    # Delete the command message
    try:
        await update.message.delete()
    except:
        pass  # Ignore errors if message can't be deleted

    # Send the target word to the admin's DM
    target_word = context.chat_data["target_word"]
    await context.bot.send_message(
        chat_id=user_id,  # Send to the admin's private chat
        text=f"🔍 The target word for the current game in this chat is: `{target_word}`"
    )

# Command: /end
async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "target_word" not in context.chat_data:
        await update.message.reply_text("You don't have an active game to end.")
        return

    # Clear game data
    context.chat_data.clear()
    await update.message.reply_text("Your current game has been ended. Use /new to start a new game.")

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Toji • Fushiguro Commands:\n"
        "/start - Start the bot and see the welcome message\n"
        "/new - Start a new word guessing game\n"
        "/end - End the current game\n"
        "/hint <position> - Get a hint for a specific letter (costs 1 point)\n"
        "/addword <word> - (Admin) Add a word to the list\n"
        "/delword <word> - (Admin) Remove a word from the list\n"
        "/checkword <word> - Check if a word exists in the bot's word list\n"
        "/leaderboard - View the global leaderboard\n"
        "/help - Show this help message"
    )

# Command: /hint <letter_position>
async def hint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Check if a game is active in this chat
    if "target_word" not in context.chat_data:
        await update.message.reply_text("No active game in this chat. Start a new game with /new.")
        return

    # Check if the user has enough points
    scores = load_scores()
    user_score = scores.get(user_id, 0)
    if user_score < 1:
        await update.message.reply_text("You don't have enough points to use this hint.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /hint <letter_position> (e.g., /hint 1 for the first letter)")
        return

    try:
        letter_position = int(context.args[0]) - 1  # Convert to 0-based index
    except ValueError:
        await update.message.reply_text("Invalid position. Please provide a number (e.g., /hint 1).")
        return

    target_word = context.chat_data["target_word"]
    if letter_position < 0 or letter_position >= len(target_word):
        await update.message.reply_text(f"Invalid position. The word has {len(target_word)} letters.")
        return

    # Deduct 1 point from the user's score
    user_score -= 1
    save_scores(user_id, user_score)

    # Send the hint to the user's PM/DM
    hint_letter = target_word[letter_position]
    await context.bot.send_message(
        chat_id=user_id,  # Send to the user's private chat
        text=f"🔍 Hint: The letter at position {letter_position + 1} is '{hint_letter.upper()}'."
    )

    await update.message.reply_text("Hint sent to your PM/DM. 1 point deducted from your score.")

# Command: /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    allowed_user_ids = [6346273488, 8171988347]  # Admin user IDs

    # Check if the user is authorized
    if user_id not in allowed_user_ids:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    # Fetch statistics from MongoDB
    users_count = scores_collection.count_documents({})  # Total users with scores
    chats_count = chats_collection.count_documents({})  # Total chats

    # Send statistics with emojis
    await update.message.reply_text(
        f"📊 Bot Statistics:\n"
        f"👤 Users: {users_count}\n"
        f"💬 Chats: {chats_count}"
    )

# Command: /broadcast <message> or reply to a message
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    allowed_user_ids = [6346273488, 8171988347]  # Admin user IDs

    # Check if the user is authorized
    if user_id not in allowed_user_ids:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    # Check if the command is used with a message or as a reply
    if update.message.reply_to_message:
        # Use the replied message as the broadcast message
        broadcast_message = update.message.reply_to_message.text
    elif context.args:
        # Use the arguments as the broadcast message
        broadcast_message = " ".join(context.args)
    else:
        await update.message.reply_text("Usage: /broadcast <message> or reply to a message.")
        return

    # Fetch all user IDs from the scores collection
    user_ids = [doc["user_id"] for doc in scores_collection.find({}, {"user_id": 1})]

    # Send the broadcast message to all users
    success_count = 0
    fail_count = 0

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Broadcast:\n{broadcast_message}")
            success_count += 1
        except Exception as e:
            print(f"Failed to send message to {uid}: {e}")
            fail_count += 1

    # Send broadcast statistics to the admin
    await update.message.reply_text(
        f"📤 Broadcast Results:\n"
        f"✅ Successfully sent to: {success_count} users\n"
        f"❌ Failed to send to: {fail_count} users"
    )

# Add handlers to the application
application.add_handler(CommandHandler("gamestart", start))
application.add_handler(CommandHandler("new", new_game))
application.add_handler(CommandHandler("end", end_game))
application.add_handler(CommandHandler("hint", hint))
#application.add_handler(CommandHandler("stats", stats))
#application.add_handler(CommandHandler("broadcast", broadcast))
#application.add_handler(CommandHandler("bcast", broadcast))
application.add_handler(CommandHandler("check", check_word))
application.add_handler(CommandHandler("addword", add_word))
application.add_handler(CommandHandler("delword", del_word))
application.add_handler(CommandHandler("checkword", check_word_exists))
application.add_handler(CommandHandler("leaderboard", leaderboard))
application.add_handler(CommandHandler("gamehelp", help_command))

# Callback query handler for word length selection
application.add_handler(CallbackQueryHandler(select_length))

# Message handler for word guesses
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
