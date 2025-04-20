import pyautogui
import time
import pytesseract
from PIL import Image, ImageEnhance
from typing import Tuple, Optional
from datetime import datetime
import pytz

# Coordinates from your input
PAIR_SELECTOR = (263, 143)
INPUT_PAIR = (521, 222)
BUY_BUTTON = (1688, 357)
SELL_BUTTON = (1650, 455)
AMOUNT_BUTTON = (1686, 222)
RESET_POPUPS = (1700, 726)

# Base initial amount (modify this to change the starting amount)
BASE_INITIAL_AMOUNT = 1
STOP_LOSS = 128
INITIAL_AMOUNT = BASE_INITIAL_AMOUNT  # This will be updated dynamically

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_closest_position(image: str, ref_pos: Tuple[int, int], region: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
    """Find the closest instance of an image to a reference position within a region."""
    locations = list(pyautogui.locateAllOnScreen(image, confidence=0.8, region=region))
    if not locations:
        return None
    
    ref_x, ref_y = ref_pos
    closest = None
    min_distance = float('inf')
    
    for loc in locations:
        center_x = loc.left + loc.width // 2
        center_y = loc.top + loc.height // 2
        distance = ((center_x - ref_x) ** 2 + (center_y - ref_y) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest = (center_x, center_y)
    
    return closest

def select_trading_pair(trading_pair: str) -> bool:
    """Selects the trading pair and chooses the OTC option if the pair exists."""
    pyautogui.click(PAIR_SELECTOR)
    time.sleep(0.2)
    pyautogui.click(INPUT_PAIR)
    time.sleep(0.1)
    pyautogui.typewrite(trading_pair)
    time.sleep(0.5)

    try:
        not_found = pyautogui.locateOnScreen('assets/not_found.png', confidence=0.8)
        if not_found:
            print(f"Trading pair '{trading_pair}' not found!")
            return False
    except pyautogui.ImageNotFoundException:
        print("Currency Pair found, continuing...")

    region = (INPUT_PAIR[0] - 50, INPUT_PAIR[1], 300, 200)
    otc_position = find_closest_position('assets/otc_text.png', INPUT_PAIR, region)
    if otc_position:
        pyautogui.click(otc_position)
        time.sleep(0.2)
        print(f"Selected '{trading_pair} OTC'")
    else:
        print(f"'{trading_pair} OTC' not available.")
        return False

    pyautogui.click(RESET_POPUPS)
    time.sleep(0.2)
    return True

def check_trade_result() -> bool:
    """Checks for trade result popup and returns True for win, False for loss."""
    interval = 0.3
    print("Waiting for trade result...")
    popup_region = (111, 848, 240, 140)

    while True:
        screenshot = pyautogui.screenshot(region=popup_region)
        screenshot.save("assets/temp_popup.png")

        # Preprocess the image to improve OCR accuracy
        image = Image.open("assets/temp_popup.png")
        # Convert to grayscale and increase contrast
        image = image.convert('L')  # Grayscale
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # Increase contrast
        image.save("assets/temp_popup.png")

        # Use Tesseract with a custom configuration for better digit recognition
        text = pytesseract.image_to_string(
            image,
            config='--psm 6 -c tessedit_char_whitelist=$0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ).strip().lower()
        print(f"OCR Text: {text}")

        if "payout" in text:
            lines = text.split('\n')
            payout_value = None
            found_payout_line = False

            for i, line in enumerate(lines):
                if "payout" in line:
                    found_payout_line = True
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line:
                            values = next_line.split()
                            if values:
                                payout_value = values[0]
                                break
                    break

            if found_payout_line and payout_value:
                print(f"Payout Value: {payout_value}")
                # Validate payout_value: it should start with '$' and be a number
                if not payout_value.startswith('$'):
                    print("Invalid payout format (does not start with $), retrying...")
                    time.sleep(interval)
                    continue

                # Remove the '$' and try to convert to float
                try:
                    numeric_value = float(payout_value.replace('$', ''))
                    if numeric_value == 0:
                        print("Trade was unsuccessful (Payout: $0).")
                        return False
                    else:
                        print(f"Trade was successful (Payout: {payout_value})!")
                        return True
                except ValueError:
                    print("Invalid payout format (not a number), retrying...")
                    time.sleep(interval)
                    continue
            else:
                print("Payout value not found, retrying...")

        time.sleep(interval)

def modify_trade_amount(amount: int) -> None:
    """Modifies the trade amount in the UI."""
    pyautogui.click(AMOUNT_BUTTON)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('backspace')
    time.sleep(0.2)
    pyautogui.typewrite(str(amount))
    time.sleep(0.2)
    pyautogui.click(RESET_POPUPS)
    time.sleep(0.2)

def place_trade(direction: str) -> None:
    """Places a trade in the specified direction."""
    if direction.lower() == "buy":
        pyautogui.click(BUY_BUTTON)
        print("Buy trade placed!")
    elif direction.lower() == "sell":
        pyautogui.click(SELL_BUTTON)
        print("Sell trade placed!")
    else:
        raise ValueError("Direction must be 'buy' or 'sell'")
    time.sleep(2)

def wait_until_trade_time(trade_time_str: str, message_timezone: str = "Etc/GMT+3") -> None:
    """Waits until the specified trade time (in message timezone) before proceeding."""
    trade_time_dt = datetime.strptime(trade_time_str, "%H:%M")
    trade_time = trade_time_dt.time()  # Extract the time part (e.g., 20:30:00)

    # Get the current time in the message timezone (UTC-3)
    message_tz = pytz.timezone(message_timezone)
    now_utc = datetime.now(pytz.UTC)
    now_in_message_tz = now_utc.astimezone(message_tz)

    # Combine the trade time with the current date in message timezone
    trade_date = now_in_message_tz.date()
    trade_datetime = datetime.combine(trade_date, trade_time)
    trade_datetime = message_tz.localize(trade_datetime)

    # Calculate the delta between the trade time and the current time
    delta_seconds = (trade_datetime - now_in_message_tz).total_seconds()
    
    UI_ACTION_TIME = 1.0  # Total time for modify_trade_amount (5 * 0.2 seconds)
    if delta_seconds <= 0:
        print(f"Trade time {trade_time_str} (UTC-3) is in the past. Executing trade immediately.")
    else:
        trade_datetime_utc = trade_datetime.astimezone(pytz.UTC)
        print(f"Current time (UTC): {now_utc.strftime('%H:%M:%S')}")
        print(f"Trade time (UTC-3): {trade_time_str}, which is {trade_datetime_utc.strftime('%H:%M:%S')} UTC")
        print(f"Waiting for {delta_seconds:.0f} seconds until trade time...")
        time.sleep(max(0, delta_seconds - UI_ACTION_TIME))

def execute_trade_sequence(direction: str, max_attempts: int = 3) -> None:
    """Executes a trade sequence with retries on loss, keeping the same direction."""
    global INITIAL_AMOUNT
    attempts = 0
    gale_amount = INITIAL_AMOUNT

    while attempts < max_attempts:
        attempts += 1
        print(f"\nTrade Attempt {attempts}/{max_attempts} (Direction: {direction.capitalize()}, Amount: ${gale_amount})")
        
        modify_trade_amount(gale_amount)
        place_trade(direction)
        result = check_trade_result()
        
        if result:
            print("Trade sequence successful! Stopping.")
            INITIAL_AMOUNT = BASE_INITIAL_AMOUNT
            modify_trade_amount(INITIAL_AMOUNT)
            return
        
        if attempts < max_attempts:
            print(f"Trade failed. Retrying ({max_attempts - attempts} attempts left)...")
            gale_amount *= 2
        else:
            print("Max attempts reached. Trade sequence failed.")
            INITIAL_AMOUNT = gale_amount * 2
            if INITIAL_AMOUNT > STOP_LOSS:
                print(f"INITIAL_AMOUNT ${INITIAL_AMOUNT} exceeds maximum limit of ${STOP_LOSS}. Resetting to BASE_INITIAL_AMOUNT.")
                INITIAL_AMOUNT = BASE_INITIAL_AMOUNT
            modify_trade_amount(INITIAL_AMOUNT)
            return

def execute_trade_with_parameters(trading_pair: str, trade_time: str, direction: str) -> bool:
    """Executes a trade with the specified parameters."""
    # Normalize trading_pair by removing extra spaces around the slash
    trading_pair = '/'.join(part.strip() for part in trading_pair.split('/'))
    
    print("Starting in 5 seconds... Switch to Pocket Option!")
    time.sleep(5)

    if not select_trading_pair(trading_pair):
        print("Failed to select trading pair or OTC not available.")
        return False

    wait_until_trade_time(trade_time, message_timezone="Etc/GMT+3")
    execute_trade_sequence(direction, max_attempts=3)
    return True