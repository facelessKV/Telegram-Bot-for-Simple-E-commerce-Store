🔥 Telegram-Bot-for-Simple-E-commerce-Store

Want to sell products via Telegram? 🚀
Your customers are already on Telegram! But how do you set up an easy ordering process without complex websites?

✅ The solution – this bot!

With this bot, you can create a simple online store directly in Telegram. Your customers will be able to:

• 📜 Browse the product catalog
• 🛒 Add items to the cart
• 💳 Place orders right in the chat
• 🔔 Receive order status updates

🔧 Features

✅ Database support for storing products and orders
✅ User-friendly admin panel for order management
✅ Automated notifications about purchase status

📩 How to get this bot?

Just message me on Telegram, and I'll help you launch a full-fledged store right in your chat! 🚀

# INSTRUCTIONS FOR INSTALLING AND LAUNCHING THE STORE TELEGRAM BOT

## WHAT DOES THIS BOT DO?

This bot is a simple store in Telegram, where users can:
- View products in the catalog
- Add products to the cart
- Place orders
- The administrator receives notifications about new orders

## INSTALLATION ON WINDOWS

### Step 1: Install Python

1. Download Python 3.10 from the official website: https://www.python.org/downloads/release/python-31011/
(Scroll down and select "Windows installer (64-bit)")

2. Run the downloaded installation file
- Be sure to check the "Add Python to PATH" box
- Click "Install Now"

3. Wait for the installation to complete

### Step 2: Downloading bot files

1. Create a folder for the bot on your computer, for example, C:\TelegramBot

2. Save the `telegram_shop_bot.py` file to this folder

### Step 3: Installing the required libraries

1. Open the Windows command prompt:
- Press Win+R
- Type cmd and press Enter

2. In the command prompt that opens, go to the folder with the bot:
```
cd C:\TelegramBot
```

3. Install the required libraries by entering the command:
```
pip install aiogram==3.0.0
```

### Step 4: Getting the Telegram bot token

1. Open Telegram and find the @BotFather bot

2. Send a message /newbot

3. Follow the instructions from BotFather:
- Enter the name of the bot
- Enter the username for the bot (must end with "bot")

4. BotFather will send you a token like 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ

5. Copy this token

### Step 5: Setting up the bot

1. Open the `telegram_shop_bot.py` file in the Notepad text editor:
- Find the line `API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'`
- Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your token from BotFather

2. To find out your ID (for admin):
- Find the @userinfobot bot in Telegram
- Send it any message
- It will reply you with your ID

3. Return to the `telegram_shop_bot.py` file:
- Find the line `ADMIN_ID = 12345678`
- Replace 12345678 with your ID from the previous step

4. Save the changes to the file

### Step 6: Running the bot

1. Open the Windows command prompt (if closed):
- Press Win+R
- Type cmd and press Enter

2. Go to the folder with the bot:
```
cd C:\TelegramBot
```

3. Run the bot by entering the command:
```
python telegram_shop_bot.py
```

4. If everything is done correctly, the command line will show information about the bot launch

5. Now go to Telegram and find your bot by the username you specified in BotFather

6. Send the bot the /start command and start using

7. To stop the bot, go back to the command line and press Ctrl+C

## INSTALLATION ON LINUX

### Step 1: Install Python

1. Open a terminal (usually Ctrl+Alt+T)

2. Update the package list:
```
sudo apt update
```

3. Install Python 3.10:
```
sudo apt install python3.10 python3.10-venv python3-pip
```

### Step 2: Creating a folder for the bot

1. Create a folder for the bot:
```
mkdir ~/telegram_bot
```

2. Go to this folder:
```
cd ~/telegram_bot
```

### Step 3: Creating a file with the bot code

1. Launch a text editor to create a file:
```
nano telegram_shop_bot.py
```

2. Paste the bot code (the contents of the telegram_shop_bot.py file) into the editor that opens

3. Save the file by pressing Ctrl+O, then Enter, and exit the editor by pressing Ctrl+X

### Step 4: Installing the necessary libraries

1. While in the folder with the bot, run the command:
```
pip3 install aiogram==3.0.0
```

### Step 5: Getting a Telegram bot token

1. Open Telegram and find the @BotFather bot

2. Send a message to /newbot

3. Follow BotFather's instructions:
- Enter the bot name
- Enter the username for the bot (must end with "bot")

4. BotFather will send you a token like 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ

5. Copy this token

### Step 6: Setting up the bot

1. Open the bot file in an editor:
```
nano telegram_shop_bot.py
```

2. Find the line `API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'`

3. Replace 'YOUR_TELEGRAM_BOT_TOKEN' to your token from BotFather

4. To find out your ID (for admin):
- Find the @userinfobot bot in Telegram
- Send it any message
- It will reply with your ID

5. Find the line `ADMIN_ID = 12345678`

6. Replace 12345678 with your ID from the previous step

7. Save the changes by pressing Ctrl+O, then Enter, and exit the editor by pressing Ctrl+X

### Step 7: Launching the bot

1. While in the folder with the bot, run the command:
```
python3 telegram_shop_bot.py
```

2. If everything is done correctly, information about the bot launch will appear in the terminal

3. Now go to Telegram and find your bot by the username you specified in BotFather

4. Send bot command /start and start using

5. To stop the bot, go back to the terminal and press Ctrl+C

## ADDITIONAL: HOW TO MAKE THE BOT RUNNING ALL THE TIME

### On Windows:

1. Create the file `start_bot.bat` in the same in the folder where `telegram_shop_bot.py` is located

2. Open this file in Notepad and add the following line to it:
```
python telegram_shop_bot.py
```

3. Save the file

4. Now you can run the bot by simply double-clicking the `start_bot.bat` file

### On Linux:

1. Install the screen program:
```
sudo apt install screen
```

2. Start a new screen session:
```
screen -S telegram_bot
```

3. Run the bot:
```
python3 telegram_shop_bot.py
```

4. Press Ctrl+A, then D to detach from the screen session (the bot will continue to run)

5. To return to the bot later, type:
```
screen -r telegram_bot
```

## POSSIBLE PROBLEMS AND SOLUTIONS

1. **Error "ModuleNotFoundError: No module named 'aiogram'"**
- Try installing the library again: `pip install aiogram==3.0.0` (Windows) or `pip3 install aiogram==3.0.0` (Linux)

2. **Bot does not respond after launch**
- Check if you entered the BotFather token correctly
- Make sure your internet connection is working
- Check if there are any errors in the command line/terminal

3. **Error "sqlite3.OperationalError: unable to open database file"**
- Make sure you have write access to the folder with the bot
- On Linux, you may need to run: `chmod 755 ~/telegram_bot`

4. **Other errors**
- Copy the error text from the command line/terminal
- Use an internet search or ask from a specialist
