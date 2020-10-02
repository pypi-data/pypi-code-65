def curvefit(ftoread,ftowrite,ts=1000):

    from scipy.optimize import curve_fit as cvf
    import numpy as np
    import csv
    import matplotlib.pyplot as plt
    
    csvName = ftoread
    
    csv_file = open(csvName,"r")
    csv_input = csv.reader(csv_file)
    
    arr = []
    cof = 0
    dens_coef = 5
    ts = ts + 50
    for row in csv_input:
        cof +=1
        if cof<=ts:
            arr.append(row)
    csv_file.close()
    
    arr = np.array(arr)
    
    nrow,ncol = arr.shape
    
    exp = int(nrow/dens_coef)
    init_btf = float(arr[1,1])
    
    time = np.zeros(exp)
    value = np.zeros(exp)
    
    tm = np.linspace(0,ts-dens_coef,exp)
    
    
    for i in range(exp):
        time[i] = arr[i*dens_coef+1,0]
    
    w = tm.reshape(exp,1)
    
    toff = np.ones(ncol)

    tt = -1
    for j in range(ncol):
        tt+=1
        for i in range(1,exp):
            value[i-1] = arr[i*dens_coef,j]
            
        def func(x, a, b,c ,d):
            return a - b*np.log(x+d)+c*x**0.25
        
        popt,pcov = cvf(func,time,value, p0 = [0,-30,30,+30] ,maxfev = 1000000)
        value_fit = func(tm,*popt)
        
        ii = -1
        for o in value_fit:
            ii+=1
            e = np.e
            tau = init_btf/e
            if o > tau -0.5 and o < tau+0.5 :
                toff[tt] = tm[ii]
                
            elif o > tau-1 and o < tau+1:
                toff[tt] = tm[ii]
                
            elif o > tau-1.5 and o < tau+1.5:
                toff[tt] = tm[ii]
                break
        print(toff)
            
        value_fit[0] = init_btf
        value_fit = value_fit/init_btf
        
        value_fit =value_fit.reshape(exp,1)
    
        if j == 0:
            pass
        else:
            w = np.append(w,value_fit,axis=1)
    
    # plt.plot(time,value/init_btf,"b.", label= "real")
    # plt.plot(tm,value_fit, "r-", label = "fit")
    # plt.show()
    
    arr3 = []
    zero = -1
    delim = int(ts/50-1)
    for k in w:
        zero +=1
        if zero%delim == 0:
            arr3.append(k)
    
    arr4 = []
    i =0
    while(w[i][0]<=ts-50 and i<len(w)):
        arr4.append(w[i])
        i+=1
    
    toff = 1/toff
    toff = toff.reshape([1,ncol])
    ff = "off" + ftowrite
    np.savetxt(ff,toff,fmt= "%s",delimiter=",")
    print("done " + ff)
    
    arr4 = np.array(arr4)
    orig = "ori" + ftowrite
    np.savetxt(orig,arr4,fmt= "%s",delimiter=",")
    print("done " + orig)
    
    arr3 = np.array(arr3)
    np.savetxt(ftowrite,arr3,fmt= "%s",delimiter=",")
    print("done " +  ftowrite + "\n")
    return toff

# if __name__ == "__main__":
#     a = curvefit("c1pc350.csv", "2222.csv",2000)