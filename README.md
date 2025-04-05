# Teletrade 🚀

**Teletrade** is an automated trading bot that integrates with Telegram and the Pocket Option trading platform. It listens for trade signals in a specified Telegram channel, extracts relevant information (currency pair, time, and direction), and executes trades using UI automation. The bot implements a Martingale (Gale) strategy to handle losses, making it a powerful tool for binary options trading.

## Features ✨

- **Telegram Integration**: Listens for trade signals in a specified Telegram channel.
- **UI Automation**: Executes trades on the Pocket Option platform using `pyautogui`.
- **Martingale Strategy**: Automatically retries trades with doubled amounts on losses (up to a configurable number of attempts).
- **OCR for Trade Results**: Uses Tesseract OCR to read trade results from the Pocket Option UI.
- **Customizable Regex**: Easily modify regex patterns to match different Telegram message formats.
- **Channel ID Retrieval**: Includes a utility script to fetch Telegram channel IDs.

## Project Structure 📂
```
Teletrade/
├── scripts/
│   ├── init.py
│   ├── main.py              # Main script to listen for Telegram messages and execute trades
│   ├── trader.py            # Trade execution logic with UI automation
│   └── get_channel_ids.py   # Script to retrieve Telegram chat IDs
├── scripts_for_checking/
│   ├── init.py
│   └── check_trader.py      # Script to synchronously test trader.py
├── data/
│   ├── secrets.csv          # Telegram API credentials (api_id, api_hash, phone_number)
│   └── session_name.session # Telegram session file (auto-generated)
├── assets/
│   ├── not_found.png        # Image for detecting unavailable trading pairs
│   ├── otc_text.png         # Image for selecting OTC pairs
│   └── temp_popup.png       # Temporary screenshot for OCR
├── README.md                # Project documentation (you're reading it!)
└── requirements.txt         # List of Python dependencies
```

## Prerequisites 📋

Before you begin, ensure you have the following:

- **Python 3.8+**: Installed on your system.
- **Pocket Option Account**: We use Pocket Option for trading. Ensure you have an account and the platform open during trading.
- **Telegram Account**: You’ll need a Telegram account and access to a channel with trade signals.
- **Tesseract-OCR**: Required for reading trade results from the Pocket Option UI.

## Setup ⚙️

### 1. Clone the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/Teletrade.git
cd Teletrade
```
### 2. Install Dependencies
Install the required Python packages using the provided requirements.txt:

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract-OCR
- Windows:
    - Download and install tesseract-OCR from [here](https://github.com/UB-Mannheim/tesseract/wiki)
    - Ensure the Tesseract executable is in your PATH, or update the path in trader.py

    
    ```
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ```

- Linux:
    ```
    sudo apt-get install tesseract-ocr
    ```

- macOS:
    - Install via Homebrew:
    ```
    brew install tesseract
    ```


### 4. Prepare secrets.csv
The bot uses Telegram’s API to listen for messages. You’ll need to provide your API credentials in data/secrets.csv.

- Create the file data/secrets.csv with the following format

```
api_id,api_hash,phone_number
your_api_id,your_api_hash,+your_phone_number
```

- **How to get your API Credentials**
    1. Go to [my.telegram.org](https://my.telegram.org/) and log in with your Telegram account.
    2. Click on “API development tools” and create a new application.
    3. Note down your api_id and api_hash.
    4. Use your phone number in international format (e.g., +1234567890).

**Important: Fill the secrets.csv file with your own data. Do not share this file publicly, as it contains sensitive information.**

### 5. Prepare Image Assets

The bot uses UI automation and relies on image recognition to interact with Pocket Option. Ensure the following images are in the assets/ directory:

- `not_found.png`: A screenshot of the “Not Found” message that appears when a trading pair is unavailable.

- `otc_text.png`: A screenshot of the “OTC” text in the trading pair dropdown.

## Configuration 🛠️

### 1. Update the Telegram Channel ID

The bot listens for trade signals in a specific Telegram channel. The default channel ID is set in `scripts/main.py`:

```
channel = 0
```
- Replace the channel ID:
    - Run the `get_channel_ids.py` script to find the ID of your Telegram channel:

    ```
    python scripts/get_channel_ids.py
    ```

    - This will list all your Telegram chats and their IDs. Look for your channel’s ID (it will start with `-100` for channels, e.g., `-1001234567..`).

    - Update the channel variable in `scripts/main.py` with your channel’s ID.

### 2. Modify the Regex Pattern (if needed)
The bot uses regex patterns to extract trade information from Telegram messages. The patterns are defined in scripts/main.py:

```
pattern_1 = re.compile(
    r"([A-Z]{3}/[A-Z]{3});\s*(\d{2}:\d{2});\s*(PUT|CALL)\s*[🟥🟩]", re.IGNORECASE
)
pattern_2 = re.compile(
    r"([A-Z]{3}\s*/\s*[A-Z]{3})\s*$$ OTC $$?-\s*(\d{2}:\d{2})\s*(PUT|CALL)\s*[🔴🟢]", re.IGNORECASE
)
```

### 3. Adjust Trading Parameters (Optional)

You can customize the trading parameters in `scripts/trader.py`:

- **Initial Amount**
```
BASE_INITIAL_AMOUNT = 1
```

- **Stop loss**
```
STOP_LOSS = 128
```

- **Max Attempts for Martingale**
```
max_attempts = 3  # In execute_trade_sequence()
```

## Usage 🚀

### 1. Test the trader script

Before running the bot with Telegram, test the trader.py script to ensure it works with Pocket Option:

```
python scripts/check_trader.py
```

- This script synchronously executes a trade with hardcoded values.
- Ensure Pocket Option is open and visible on your screen.
- Adjust the `trade_time` in `check_trader.py` to a few minutes in the future (e.g., if it’s 16:40, set it to 16:45).

### 2. Run the Bot

Start the bot to listen for telegram messages and execute trades:

```
python scripts/main.py
```

- The bot will connect to Telegram and listen for messages in the specified channel.

- When a message matching one of the regex patterns is received `(e.g., USD /BDT(OTC)-07:35 CALL)`, it will:
    1. Extract the currency pair, time, and direction.
    2. Wait until the specified time.
    3. Execute the trade on Pocket Option using the Martingale strategy.

### **Important Notes**

- Pocket Option: We use Pocket Option for trading. Ensure the platform is open and maximized on your screen during trading.

- UI Automation: The bot uses pyautogui for UI automation. Do not move the mouse or use the keyboard while trades are being executed, as this may interfere with the bot.

- Screen Resolution: The bot’s UI coordinates (in trader.py) are hardcoded for a specific screen resolution. If your resolution differs, you may need to update the coordinates (e.g., PAIR_SELECTOR, BUY_BUTTON).

- Timing: The bot is optimized to minimize delays between trades in the Martingale sequence, ensuring you don’t miss the next trade window.

## Happy Trading! 📈