import time
import line_alert

time_info = time.gmtime()

m_hour = time_info.tm_hour
m_min = time_info.tm_min

print(m_hour, " ", m_min)

line_alert.SendMessage("Bithumb Server is OK!")