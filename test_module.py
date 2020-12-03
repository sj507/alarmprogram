import CA3
import time_conversions


assert CA3.announce('alarm','weather') == ''
assert CA3.weather_briefing('ff29ab5cf9b7c5aa26d00560b9d4e5f6','Exeter') == type(str)
assert time_conversions.hhmm_to_seconds('0813') == type(int)
assert time_conversions.hhmm_to_seconds('0813') == 29580
assert time_conversions.hhmmss_to_seconds('113423') == type(int) 
assert time_conversions.hhmmss_to_seconds('113423') == 41663
assert time_conversions.hours_to_minutes('7') == type(int)
assert time_conversions.hours_to_minutes('7') == 420
assert time_conversions.minutes_to_seconds('54') == type(int)
assert time_conversions.minutes_to_seconds('54') == 3240

'''
    In addition to this System and Acceptance testing were performed to make sure that the program functioned as expected
'''
