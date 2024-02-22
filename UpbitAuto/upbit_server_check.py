import line_alert
import time

time_info = time.gmtime()
m_hour = time_info.tm_hour

# 7시에 메시지를 보냅니다
if m_hour == 22:
    line_alert.SendMessage("Upbit Server is OK")