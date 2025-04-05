# import pyautogui, time
# while True:
#     time.sleep(1)  # Move mouse over "Trade closed" text
#     print(pyautogui.position())

from trader import execute_trade_with_parameters

trading_pair = "CAD/JPY"
trade_time = "06:35"  # In UTC-3
direction = "buy"

# Execute the trade
success = execute_trade_with_parameters(trading_pair, trade_time, direction)
if success:
    print("Trade execution completed successfully.")
else:
    print("Trade execution failed.")

