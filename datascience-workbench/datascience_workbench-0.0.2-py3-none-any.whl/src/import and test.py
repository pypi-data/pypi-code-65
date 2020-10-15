from Time import Time as t
from Lists import Lists as l
from Processing import Processing as p
 

### PROCESSING
# get all files from a directory (default is current directory)
print(p.get_files())



int_list = [i for i in range(20)]
str_list = [s for s in "abcdefg"]



### LISTS
# create batches
batched = [i for i in l.batch(int_list)]
print("Batched list: {}".format(batched))




### TIME 
# Timeout with printed countdown
t.sleep_countdown(1, print_step=1)

# current timestamp
print("Current timestamp: {}".format(t.timestamp_now()))

# add years to date
from datetime import datetime

d = datetime.datetime(1970, 1, 1)
d_plus = t.date_add_year(d, 2)

print(d)
print(d_plus)