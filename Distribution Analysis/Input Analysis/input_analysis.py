#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
from fitter import Fitter
# import xlrd
#%%
# Read the data from the Excel file
df : pd.DataFrame = pd.read_excel('data.xls').T
df.reset_index(inplace=True)
df.columns = df.iloc[0]
df = df.drop(df.index[0])
df = df.astype(float)
#%%
def plot_hist(data, title : str, x_label : str, y_label : str, bins : int = 40):
    plt.figure(figsize=(10, 6))
    sns.histplot(data, color='blue', bins=bins)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()
#%% md
# We assume that the interarrival times follow an exponential distribution.
# We will test the hypothesis that the service times for the initial phase,
# are uniformly distributed.
# We will test the hypothesis that the service times for placing the keyboard and mouse,
# follow a normal distribution.
# We will test the hypothesis that the service times for assembling the case (aluminum plates),
# are exponentially distributed.
#%% md
# Stat the null and alternative hypotheses
# H0: The interarrival times follow an exponential distribution
# H1: The interarrival times do not follow an exponential distribution
# Find a test statistic
#   Find the empirical pdf (histogram) by specifying the number of equal bins k
#   Measure the distance between the empirical pdf (histogram) and expected pdf (histogram)
# Find a rejection region
#   If the distance is greater than a pre-specified value reject the null hypothesis
# The distance between the empirical pdf and observed pdf?
# n data points
# Partition the support into k bins
#   If the support is unbounded, we can have a_0 = -inf or a_k = inf
# Find the expected number of observations (E_i) in each bin i and
# the actual number of observations (O_i)
# How do we find the expected number of observations in each bin?
#   First find the probability of an observation falling in each bin
#   p_i = F(a_i) - F(a_{i-1})
#   E_i = n*p_i (Choose k, a_i so that E_i \ge 5)
# Find the observed number of observations in each bin by counting the data
# Test statistic: Normalized square distance between the observed and expected number of observations
#   D = sum_{i=1}^{k} (O_i - E_i)^2/E_i
#   D ~ chi-square(k-1, 1 - \alpha)
#   Reject H0 if D > chi-square(k-1, 1 - \alpha)
#%%
def chi_square_test(data, cdf, alpha=0.05):
    n = len(data)
    # Determine the number of bins
    k = int(np.floor(n/ 5))
    # Determine the bin edges
    bin_edges = np.linspace(min(data), max(data), k + 1)
    # Determine the expected number of observations in each bin
    p = np.zeros(k)
    e = np.zeros(k)
    o = np.zeros(k)
    for i in range(k):
        p[i] = cdf(bin_edges[i+1]) - cdf(bin_edges[i])
        e[i] = n*p[i]
        o[i] = np.sum((data >= bin_edges[i]) & (data < bin_edges[i + 1]))
    test_statistic = np.sum((o - e)**2/e)
    chi_square = stats.chi2.ppf(1 - alpha, k - 1)
    # Display the results
    print(f'Test statistic = {test_statistic:.2f}, chi-square = {chi_square:.2f}')
    if test_statistic > chi_square:
        print('Reject H0')
    else:
        print('Do not reject H0')
    return {'D': test_statistic, 'chi_square': chi_square, 'k': k, 'p': p, 'E': e, 'O': o}
#%%
# Testing the hypothesis that the interarrival times follow an exponential distribution
def exponential_cdf(x_, lambda_):
    return 1 - np.exp(-lambda_*x_)

interarrival_times = df['Interarrival Times']
# curry the exponential_cdf function with lambda_ = 1/mean
mean = np.mean(interarrival_times)
exponential_cdf_ = lambda x : exponential_cdf(x, 1 / mean)

print(f'Testing the hypothesis that the interarrival times \nfollow an exponential distribution mean = {mean:.2f}')
_ = chi_square_test(interarrival_times, exponential_cdf_)

# plot_hist(interarrival_times,
#     'Histogram of Interarrival Times',
#     'Interarrival Time',
#     'Frequency')

#%%
# Testing the hypothesis that the service times for the initial phase are uniformly distributed
def uniform_cdf(x_, a_ : float, b_ : float):
    return (x_ - a_)/(b_ - a_)

initial_phase = df['Service Times for Initial Phase']
a = min(initial_phase)
b = max(initial_phase)
uniform_cdf_ = lambda x: uniform_cdf(x, a, b)

print(f'Testing the hypothesis that the service times for the \ninitial phase are uniformly distributed with a = {a:.2f} and b = {b:.2f}')
_ = chi_square_test(initial_phase, uniform_cdf_)
#%%
# Testing the hypothesis that the service times for placing the keyboard and mouse follow a normal distribution
def normal_cdf(x_, mu_, sigma_):
    return stats.norm.cdf(x_, mu_, sigma_)

def weibull_cdf(x_, shape, scale):
    return 1 - np.exp(-(x_ / scale) ** shape)

keyboard_mouse = df['Service Times for Placing Keyboard and Mouse']
mu = np.mean(keyboard_mouse)
sigma = np.std(keyboard_mouse)
normal_cdf_ = lambda x: normal_cdf(x, mu, sigma)

print(f'Testing the hypothesis that the service times for placing the \nkeyboard and mouse follow a normal distribution with μ = {mu:.2f} and σ = {sigma:.2f}')
_ = chi_square_test(keyboard_mouse, normal_cdf_) # reject H0

print(f'Testing the hypothesis that the service times for placing the \nkeyboard and mouse follow a Weibull distribution with shape = {mu:.2f} and scale = {sigma:.2f}')
#%%
distributions = ['norm', 'weibull_min']
f = Fitter(keyboard_mouse, distributions=distributions)
f.fit()
f.summary()
print(f.get_best())
f.hist()
plt.show()
#%%
# Testing the hypothesis that the service times for assembling the case (aluminum plates) are exponentially distributed
assembling_case = df['Service Times for Assembling the Case (Aluminum Plates)']

mean = np.mean(assembling_case)
exponential_cdf_ = lambda x : exponential_cdf(x, 1 / mean)

print(f'Testing the hypothesis that the service times for assembling the \ncase (aluminum plates) are exponentially distributed with mean = {mean:.2f}')
_ = chi_square_test(assembling_case, exponential_cdf_)
