arr = [1,-1,-1,1,1,1,-1,5,-1,-1,-1]

max_subarr_sum = 0
max_subarr_begin_ix = 0
max_subarr_end_ix = 0
sum_ending_here = 0
begin_ix = 0

for i in range(len(arr)):
    if sum_ending_here < 0:
        begin_ix = i
        sum_ending_here = arr[i]
    else:
        sum_ending_here += arr[i]
    if sum_ending_here > max_subarr_sum:
        max_subarr_sum = sum_ending_here
        max_subarr_begin_ix = begin_ix
        max_subarr_end_ix = i

