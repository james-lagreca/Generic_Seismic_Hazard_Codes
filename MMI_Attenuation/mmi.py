import matplotlib.pyplot as plt
import matplotlib as mpl
from numpy import arange, log10, sqrt, exp, log, where, zeros_like
mpl.style.use('classic')

plt.rcParams['pdf.fonttype'] = 42

fig = plt.figure(figsize=(10, 6))
plt.tick_params(labelsize=12)

# event details
mag = 5.9
eqdep = 12 
eqlat = -37.5063
eqlon = 146.4022
ztor = 4.
vs30 = 760  # Vs30 value in m/s
maxrrup = 1000  # Set to 200 km
rjb = arange(0.01, maxrrup + 1, 0.1)  # Values from 0 to 200 km in 1 km increments
rrup = sqrt(rjb**2 + eqdep**2)

####################################################################################
# Plot models using explicit equations

def atkinson_wald_ceus_ipe(mag, rrup):
    c1 = 11.72
    c2 = 2.36
    c3 = 0.1155
    c4 = -0.44
    c5 = -0.002044
    c6 = 2.31
    c7 = -0.479
    h  = 17.
    Rt = 80.
    sig = 0.4
    
    R = sqrt(rrup**2 + h**2)
    B = zeros_like(R)
    idx = where(R > Rt)[0]
    B[idx] = log10(R[idx] / Rt)
        
    mmi = c1 + c2 * (mag - 6) + c3 * (mag - 6)**2 + c4 * log10(R) + c5 * R + c6 * B + c7 * mag * log10(R)
    
    return mmi, sig

def atkinson_wald_cal_ipe(mag, rrup):
    c1 = 12.27
    c2 = 2.27
    c3 = 0.1304
    c4 = -1.30
    c5 = -0.0007070
    c6 = 1.95
    c7 = -0.577
    h  = 14.
    Rt = 30.
    sig = 0.4
    
    R = sqrt(rrup**2 + h**2)
    B = zeros_like(R)
    idx = where(R > Rt)[0]
    B[idx] = log10(R[idx] / Rt)
        
    mmi = c1 + c2 * (mag - 6) + c3 * (mag - 6)**2 + c4 * log10(R) + c5 * R + c6 * B + c7 * mag * log10(R)
    
    return mmi, sig

def leonard15_ipe(mw, rrup):
    c0 = 3.5
    c1 = 1.05
    c2 = -1.09
    c3 = 1.1
    
    return c0 + c1 * mw + c2 * log(sqrt(rrup**2 + (1 + c3 * exp(mw - 5))**2))

def www14_ipe(mag, rrup, vs30, region='CA'):
    from numpy import log10, sqrt, where, zeros_like
    
    # Coefficients from Worden, Wald, and others (2014)
    if region == 'CA':
        if vs30 >= 760:
            c1 = 0.309
            c2 = 1.864
            c3 = -1.672
            c4 = -0.00219
            c5 = 1.77
            c6 = -0.383
        else:
            # Coefficients for Vs30 < 760 m/s
            c1 = 0.289
            c2 = 1.784
            c3 = -1.672
            c4 = -0.00210
            c5 = 1.60
            c6 = -0.350
    elif region == 'CEUS':
        c1 = 0.7
        c2 = 1.864
        c3 = -1.672
        c4 = -0.00219
        c5 = 1.77
        c6 = -0.383
    
    h = 14.
    sig = 0.15
    
    R = sqrt(rrup**2 + h**2)
    Rt = log10(R / 50.)
    B = zeros_like(R)
    idx = where(Rt > 0)[0]
    B[idx] = Rt[idx]
        
    mmi = c1 + c2 * mag + c3 * log10(R) + c4 * R + c5 * B + c6 * mag * log10(R)
    
    return mmi, sig

# Calculate MMI for different models
AW07ceus, sig = atkinson_wald_ceus_ipe(mag, rrup)
AW07cal, sig = atkinson_wald_cal_ipe(mag, rrup)
L15 = leonard15_ipe(mag, rrup)
WWW14_CA, sig = www14_ipe(mag, rrup, vs30, region='CA')
WWW14_CEUS, sig = www14_ipe(mag, rrup, vs30, region='CEUS')

# Plot models
cl = ['b', 'g', 'r', 'c', 'm']  # Define some colors
syms = ['o', '^', 's', 'd', 'x']

h1 = plt.plot(rjb, AW07ceus, syms[0], color=cl[0], ls='-', ms=5, mec=cl[0], markevery=5)
h2 = plt.plot(rjb, AW07cal, syms[1], color=cl[1], ls='-', ms=5, mec=cl[1], markevery=5)
h3 = plt.plot(rjb, L15, syms[2], color=cl[2], ls='-', ms=5, mec=cl[2], markevery=5)
h4 = plt.plot(rjb, WWW14_CA, syms[3], color=cl[3], ls='-', ms=5, mec=cl[3], markevery=5)
h5 = plt.plot(rjb, WWW14_CEUS, syms[4], color=cl[4], ls='-', ms=5, mec=cl[4], markevery=5)

##################################################################################

leg1 = plt.legend([h1[0], h2[0], h3[0], h4[0], h5[0]], 
           ['AW07 CEUS', 'AW07 CA', 'L15 AU', 'WWW14 CA', 'WWW14 CEUS'], fontsize=12, loc=3, numpoints=1)

plt.grid(which='both', color='0.5')
plt.xlim([0, maxrrup])
plt.ylim([1, 8])
plt.xlabel('Epicentral Distance (km)', fontsize=14)
plt.ylabel('Macroseismic Intensity', fontsize=14)

xtic = [10, 20, 50, 100, 200]
xlab = ['10', '20', '50', '100', '200']
plt.xticks(xtic, xlab)
ylab = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
ytic = range(1, 9)
plt.yticks(ytic, ylab)

import pandas as pd

# Data to save
data = {
    'rjb': rjb,
    'AW07_CEUS': AW07ceus,
    'AW07_CA': AW07cal,
    'L15_AU': L15,
    'WWW14_CA': WWW14_CA,
    'WWW14_CEUS': WWW14_CEUS
}

# Create a DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('WP_attenuation_results.csv', index=False)


plt.savefig('wp_mmi_atten.png', format='png', dpi=300, bbox_inches='tight')
#plt.savefig('figures/moe_mmi_atten.svg', format='svg', dpi=300, bbox_inches='tight')

plt.show()
