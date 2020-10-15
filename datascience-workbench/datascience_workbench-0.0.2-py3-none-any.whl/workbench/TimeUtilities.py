from time import strftime
from time import sleep # sleep_countdown()
from datetime import date
import sys

class Time:
	
	def __init__(self):
		""" Convenient methods to handle date & time   
		"""


	def timestamp_now():
	    """Create timestamp string in format: yyyy/mm/dd-hh/mm/ss
	    	primaryliy used for file naming

	    Input
	        None
	        
	    Return
	        String: Timestamp for current time
	        
	    """
	    
	    timestr = strftime("%Y%m%d-%H%M%S")
	    timestamp = '{}'.format(timestr)  
	    
	    return timestamp


    

	def date_add_year(d, years):
	    """Add/subtract a year from today's date 
	    Return the same calendar date (month and day) in the
	    destination year, if it exists, otherwise use the following day
	    (e.g. changing February 29 to March 1). 
	    Source: https://stackoverflow.com/a/15743908

	    Input: 
			d: datetime, date
			years: int, number of years to add/subtract from date d
	    
	    Return:
			date: date with year added/subtracted 
	    """
	    try:
	        return d.replace(year = d.year + years)
	    except ValueError:
	        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))    


	def sleep_countdown(duration, print_step=2):
		"""Sleep for certain duration and print remaining time in steps of print_step
		
		Input
			duration: duration of timeout (int)
			print_step: steps to print countdown (int)

		Return 
			None
		"""
		sys.stdout.write("\r Seconds remaining:")

		for remaining in range(duration, 0, -1):
			# display only steps
			if remaining % print_step == 0:
			    sys.stdout.write("\r")
			    sys.stdout.write("{:2d}".format(remaining))
			    sys.stdout.flush()

			time.sleep(1)

		sys.stdout.write("\r Complete!\n")



