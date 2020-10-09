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
        print("Lower bound of CDS tenor must be greater than orequal to the lower bound of yield curve tenor.")
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


s = [0.0003,0.0010,0.0028]

print(CDS_bootstrap(s, [0.05,0.05,0.05], [1,3,5], [1,3,5], 4, 0.5)) #[0.0006, 0.00275656, 0.01181757]

print(CDS_bootstrap(s, [0.05,0.18,0.32], [1,3,5], [1,3,5], 4, 0.5)) #[0.0006, 0.00289309, 0.01857802]




