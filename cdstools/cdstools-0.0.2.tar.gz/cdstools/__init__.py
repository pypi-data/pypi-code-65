import numpy as np
import scipy.optimize as optim
import scipy.interpolate as polate


def CDS_bootstrap(cds_spreads, yield_curve, cds_tenor, yield_tenor, prem_per_year, R):
    '''
    Returns the hazard rate curve and corresponding survival probabilities 
    for a given yield curve, CDS spreads, and their corresponding tenor.
    '''
    # Checks
    if len(cds_spreads) != len(cds_tenor):
        print("CDS spread array does match CDS tenor array")
        return None

    if len(yield_curve) != len(yield_tenor):
        print("Yield curve does not match yield tenor.")
        return None
    
    if cds_tenor[0] < yield_tenor[0]:
        print("Lower bound of CDS tenor must be greater than or equal to the lower bound of yield curve tenor.")
        return None
        
    if cds_tenor[-1] > yield_tenor[-1]:
        print("Upper bound of CDS tenor must be less than or equal to the upper bound of yield curve tenor.")
        return None
        
    # Match yield tenor to CDS tenor via interpolation    
    interp = polate.interp1d(yield_tenor, yield_curve, 'quadratic')
    yield_curve = interp(cds_tenor)
    
    def bootstrap(h, given_haz, s, cds_tenor, yield_curve, prem_per_year, R):
    
        a = 1/prem_per_year
        maturities = [0] + list(cds_tenor)
        # Assumes yield curve is flat from time 0 to earliest given maturity
        
        yields = [yield_curve[0]] + list(yield_curve)    
        pmnt = 0;        dflt = 0;        auc = 0
        
        # 1. Calculate value of payments for given hazard rate curve values
        for i in range(1, len(maturities)-1):
            
            num_points = int((maturities[i]-maturities[i-1])*prem_per_year + 1)
            t = np.linspace(maturities[i-1], maturities[i], num_points) 
            r = np.linspace(yields[i-1], yields[i], num_points)
            
            for j in range(1, len(t)):
                surv_prob_prev = np.exp(-given_haz[i-1]*(t[j-1]-t[0]) - auc)
                surv_prob_curr = np.exp(-given_haz[i-1]*(t[j]-t[0]) - auc)
                
                pmnt += s*a*np.exp(-r[j]*t[j])*0.5*(surv_prob_prev + surv_prob_curr)
                dflt += np.exp(-r[j]*t[j])*(1-R)*(surv_prob_prev - surv_prob_curr)
        
            auc += (t[-1] - t[0])*given_haz[i-1]
        
        # 2. Set up calculations for payments with the unknown hazard rate value
        num_points = int((maturities[-1]-maturities[-2])*prem_per_year + 1)
        t = np.linspace(maturities[-2], maturities[-1], num_points)
        r = np.linspace(yields[-2], yields[-1], num_points)
        
        for i in range(1, len(t)):
            
            surv_prob_prev = np.exp(-h*(t[i-1]-t[0]) - auc)
            surv_prob_curr = np.exp(-h*(t[i]-t[0]) - auc)          
            pmnt += s*a*np.exp(-r[i]*t[i])*0.5*(surv_prob_prev + surv_prob_curr)
            dflt += np.exp(-r[i]*t[i])*(1-R)*(surv_prob_prev - surv_prob_curr)
        
        return abs(pmnt-dflt)
    
    haz_rates = []
    surv_prob = []
    t = [0] + list(cds_tenor)
    
    for i in range(len(cds_spreads)):
        get_haz = lambda x: bootstrap(x, haz_rates, cds_spreads[i], cds_tenor[0:i+1], yield_curve[0:i+1], prem_per_year, R)
        haz = round(optim.minimize(get_haz, cds_spreads[i]/(1-R), method='SLSQP', tol = 1e-10).x[0],8)
        cond_surv = (t[i+1]-t[i])*haz
        haz_rates.append(haz)
        surv_prob.append(cond_surv)
    
    return haz_rates, np.exp(-np.cumsum(surv_prob))



def CDS_spread(yield_curve, yield_tenor, credit_curve, credit_curve_tenor, prem_per_year, R, maturity):
    '''
    Returns the fair spread of a CDS given credit curve, yield curve, payment frequency, recovery rate, and maturity
    '''
    # Checks (couple if statements here, no biggie)
    if len(yield_curve) != len(yield_tenor):
        print('Yield curve does not match the yield tenor')
        return None
    
    if len(credit_curve) != len(credit_curve_tenor):
        print('Credit curve does not match the credit curve tenor')
        return None            
    
    if credit_curve_tenor[0] < yield_tenor[0]:
        print("Lower bound of Credit Curve tenor must be greater than or equal to the lower bound of yield curve tenor.")
        return None
        
    if credit_curve_tenor[-1] > yield_tenor[-1]:
        print("Upper bound of Credit Curve tenor must be less than or equal to the upper bound of yield curve tenor.")
        return None
    
    # I. Get survival probabilities and default probabilities using hazard rate curve
    a = 1/prem_per_year
    num_points = int(credit_curve_tenor[-1]/a + 1)
    
    t = np.linspace(0, credit_curve_tenor[-1], num_points)
    
    h = []
    index = 0;  t_index = credit_curve_tenor[index]
    for i in range(len(t)):
        if t[i] <= t_index:
            h.append(credit_curve[index])
        else:
            index += 1
            t_index = credit_curve_tenor[index]
            h.append(credit_curve[index])
        
    surv_prob = [0.0]
    for i in range(1,len(t)):
        surv_prob.append(a*h[i])
        
    surv_prob = np.exp(-np.cumsum(surv_prob))    
    default_prob = np.asarray([0] + list(-np.diff(surv_prob)))
    
    # II. Get discount factors using yield curve
    yield_func = polate.interp1d(yield_tenor, yield_curve,'quadratic')
    ti = np.linspace(credit_curve_tenor[0], credit_curve_tenor[-1], int((credit_curve_tenor[-1]-credit_curve_tenor[0])*prem_per_year+1))
    r = yield_func(ti)
    r1 = np.asarray([r[0]]*int(credit_curve_tenor[0]*prem_per_year) + list(r))
    
    t2 = np.linspace(a/2, credit_curve_tenor[-1]-a/2, num_points-1)
    r2 = yield_func(t2[prem_per_year:])
    r2 = np.asarray([r[0]]*len(t2[0:prem_per_year]) + list(r2))
    
    # III. Solve
    PV_pmnt = [np.exp(-r1[i]*t[i])*surv_prob[i] for i in range(1,len(t))] #This works 
    PV_payoff = [(1-R)*default_prob[i+1]*np.exp(-r2[i]*t2[i]) for i in range(len(t2))]
    PV_accrual = [np.exp(-r2[i]*t2[i])*0.5*a*default_prob[i+1] for i in range(len(t2))]
    
    return sum(PV_payoff)/(sum(PV_pmnt) + sum(PV_accrual))

