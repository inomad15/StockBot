import line_alert
import time

time_info = time.gmtime()
m_hour = time_info.tm_hour

abc = "상태가 양호합니다"

line_alert.SendMessage(f"Upbit Server is OK {abc}")