'''Testing module for ca3.py and time_conversions.py'''

from time_conversions import hhmmss_to_seconds
from time_conversions import hhmm_to_seconds
from time_conversions import hours_to_minutes
from time_conversions import minutes_to_seconds


assert hhmm_to_seconds('08:13') == 29580
assert hhmmss_to_seconds('11:34:23') == 41663
assert hours_to_minutes('7') == 420
assert minutes_to_seconds('54') == 3240

''' In addition to this System and Acceptance testing were performed
    to make sure that the program functioned as expected
'''
