# import pyautogui, time
# while True:
#     time.sleep(1)  # Move mouse over "Trade closed" text
#     print(pyautogui.position())

from trader import execute_trade_with_parameters
from datetime import datetime, timedelta
import pytz

now_utc = datetime.now(pytz.UTC)
message_tz = pytz.timezone("Etc/GMT+3")
now_in_message_tz = now_utc.astimezone(message_tz)

# Set trade time to 2 minutes from now
trade_time_dt = now_in_message_tz + timedelta(minutes=2)
trade_time = trade_time_dt.strftime("%H:%M")

trading_pair = "CAD/JPY"
direction = "sell"

# Execute the trade
success = execute_trade_with_parameters(trading_pair, trade_time, direction)
if success:
    print("Trade execution completed successfully.")
else:
    print("Trade execution failed.")

