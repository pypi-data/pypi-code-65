import datetime as dt

def start(summary=True, verbose=False):
	
	# Set global variables
	global checkpoints_global
	global report_global
	global realtime_global
	checkpoints_global = []
	report_global = summary
	realtime_global = verbose
	
	# Set marker
	time = dt.datetime.now()
	marker = "Process Start"
	entry = (time, marker)
	checkpoints_global.append(entry)
	
	# Print marker
	if realtime_global:
	    print(marker)
	else:
		pass


def point(marker=None):
	
	# Set marker
	time = dt.datetime.now()
	if marker:
        assert isinstance(marker, str), "POINT MARKERS MUST BE STRING TYPE"
		entry = (time, marker)
	else:
		entry = (time, None)		
	checkpoints_global.append(entry)
	
	# Print marker
	if realtime_global:
	    # Calculate elapsed time
	    marker_start = checkpoints_global[0][0]
	    marker0 = checkpoints_global[-2][0]
	    marker1 = checkpoints_global[-1][0]
	    elapsed = marker1 - marker_start
	    marker_time = marker1 - marker0
	    
	    # Compile update
	    point_number = len(checkpoints_global) - 1
	    if marker:
	    	update = f"Step {point_number}: {marker} \n Time: {marker_time} / {elapsed}"
	    else:
	    	update = f"Step {point_number}: {marker_time} / {elapsed}"
	    
	    print(update)
	else:
		pass
		
def stop():
	
	print("")
	print("###########################")
	print("Checkpoint Summary")
	
	# Set marker
	time = dt.datetime.now()
	marker = "Process Complete"
	entry = (time, marker)		
	checkpoints_global.append(entry)
	
	# Set variables
	start = checkpoints_global[0][0]
	end = checkpoints_global[-1][0]
	elapsed = end - start
	
	if report_global:
		for n in range(1,len(checkpoints_global)):
			point0 = checkpoints_global[n-1][0]
			point1 = checkpoints_global[n][0]
			time = point1 - point0
			mark = checkpoints_global[n][1]
			pct = round((time / elapsed) * 100, 1)
			
			if mark:
				step = f"{n}: {mark} | {time} / {elapsed} | {pct}%"
			else:
				step = f"{n}: {time} / {elapsed}"
				
			print(step)
			
	else:
		pass

	print("PROCESS COMPLETE")			
	print(f"TOTAL RUN TIME: {elapsed}")