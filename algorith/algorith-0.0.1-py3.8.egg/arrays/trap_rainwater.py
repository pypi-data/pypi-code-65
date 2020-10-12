import numpy as np
from typing import List

def trap(height: List[int]) -> int:
    if len(height) == 0:
        return 0
    # First get the max height
    max_ht=max(height); area = 0
    potential = np.zeros(max_ht); max_h_so_far = 0
    prev_ht = 0
    ## Now start collecting rain.
    for h in height:
        for j in range(h, max_h_so_far):
            potential[j]+=1
        
        for j in range(prev_ht,h):
            area += potential[j]
            potential[j] = 0
    
        if h > max_h_so_far:
            max_h_so_far = h
        
        prev_ht = h            
    return int(area)


def trap_w_stack(height: List[int])-> int:
    st = []; area = 0; prev_ht=0
    accu_up = 0
    for i in range(len(height)):
        h = height[i]
        if h<prev_ht:
            h_del = (prev_ht-h)
            st.append([h_del,i-1])
            print(st)
            accu_up = 0
        elif h>prev_ht:
            h_del = (h-prev_ht); accu_up=0
            slack=0
            while len(st)>0 and accu_up<h_del:
                up_move = min(st[len(st)-1][0],h_del-accu_up)
                area += (i-st[len(st)-1][1]-1)*up_move
                print((i-st[len(st)-1][1]-1)*up_move)
                accu_up += up_move
                if slack+st[len(st)-1][0]<=accu_up:
                    slack+=st[len(st)-1][0]
                    st.pop()
                else:
                    st[len(st)-1][0]-=up_move
        prev_ht = h
    return area


def trap_w_stack_leetcode(height: List[int])-> int:
    ans = 0; current = 0
    st=[]
    while (current < len(height)):
        while (len(st)>0 and height[current] > height[st[len(st)-1]]):
            top = st[len(st)-1]
            st.pop()
            if len(st)==0:
                break
            distance = current - st[len(st)-1] - 1
            bounded_height = min(height[current], height[st[len(st)-1]]) \
                            - height[top]
            print(str(current)+","+str(st[len(st)-1])+","+str(top))
            ans += distance * bounded_height
        st.append(current)
        current+=1
    return ans


def trap_w_dp_leetcode(height: List[int])-> int:
    left = 0; right = len(height) - 1
    ans = 0
    left_max = 0; right_max = 0
    while (left < right):
        if (height[left] < height[right]):
            if height[left] >= left_max:
                left_max = height[left]
            else: 
                ans += (left_max - height[left])
            left+=1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else: 
                ans += (right_max - height[right])
            right-=1
    return ans


h = [4,2,0,3,2,5]
trap_w_dp_leetcode(h)


# h = [3,1,1,0,1,3]
# trap_w_stack(h)

# h = [4,2,0,3,2,5]
# trap(h)

# h = [0,1,0,2,1,0,1,3,2,1,2,1]
# trap_w_stack(h)

h = [0,1,0,4,1,0,1,3,2,1,2,1]
trap_w_dp_leetcode(h)

