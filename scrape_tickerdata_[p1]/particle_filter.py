import filterpy as fp
import pandas as pd
import numpy as np
from yahoo_finance import Share
import datetime
from datetime import datetime
import os
#import matplotlib.pyplot as plt

from numpy.random import uniform

#####PART 1 G_H FILTER
def g_h_filter(data, g, h):#, x0 , dx, g, h, dt=1.):
    
    x0 = data[0]
    dx = 0
    dt = 1
    x = x0
    results = []
    for z in data:
        #prediction step
        x_est = x + (dx*dt)
        dx = dx

        # update step
        residual = z - x_est
        dx = dx    + h * (residual) / dt
        x  = x_est + g * residual     
        results.append(x)  
    return np.array(results)  


#######PART 2 KALMAN FILTER



def predict(pos, movement):
    return (pos[0] + movement[0], pos[1] + movement[1])

#gets the normal dist of two dists (prediction and measurement)
def gaussian_multiply(g1, g2):
    mu1, var1 = g1
    mu2, var2 = g2
    mean = (var1*mu2 + var2*mu1) / (var1 + var2)
    variance = (var1 * var2) / (var1 + var2)
    return (mean, variance)

#below: prior is a position and varience, likelyhood is measurement pos and var
def update(prior, likelihood):
    posterior = gaussian_multiply(likelihood, prior)
    return posterior

def kalman_filter(data, sensor_var, process_var):
    x0 = (data[0], 1)
    velocity = 0
    dt = 1.
    sensor_var = sensor_var
    process_var = process_var
    process_model = (velocity*dt, process_var)
    
    x = x0
    
    
    xs, predictions = [], []
    for z in data:
        prior = predict(x, process_model)
        #print(prior)
        likelihood = (z, sensor_var)
        x = update(prior, likelihood)

        # save results
        predictions.append(prior[0])
        xs.append(x[0])
    return predictions, xs



###in other 
def get_ticker_data(strat):
    ''' this should have parameters
        date range
        type of smooth val (which function)
    '''
    start = '2007-05-02'
    end = '2015-12-31'
    fin_data_path = '../fin_data/'
    path = ''.join((fin_data_path, strat, '_', start, end))
    if os.path.exists(path):
        data = pd.read_pickle(path)
    else:
        data = pd.DataFrame(Share(strat).get_historical(start, end))
        print('fetched data')
        data.Date = [datetime.strptime(data.Date.iloc[i], '%Y-%m-%d') for i in data.index]
        data.index = data.Date
        data = data.iloc[::-1]
        data.Close = [float(x) for x in data.Adj_Close]
        data.to_pickle(path)
    return data
    
def call_filters(data):
    ###calls it here!!
    data['filtered'] = g_h_filter(np.array(data.Close), g = .5, h=.5)
    data['kal_prediction'], data['kal_smooth'] = kalman_filter(np.array(data.Close), 1, .01)
    
    #data['smooth'], data['trend'] = get_smooth_val(data.Close, 50)
    #data['resid'] = data.Close-data['smooth']
    #data['dailyrets'] = get_dailyret(data.Close)
    return data



def main_test():
    data = get_dfs('GS')
    data = call_filters(data)
    print(data.head())
    print(data.tail())
    return data
    
if __name__=='__main__':
    main_test()
    
    
    
    
    
    
    
    
    
'''    
def create_uniform_particles(x_range, y_range, hdg_range, N):
    particles = np.empty((N, 3))
    particles[:, 0] = uniform(x_range[0], x_range[1], size=N)
    particles[:, 1] = uniform(y_range[0], y_range[1], size=N)
    particles[:, 2] = uniform(hdg_range[0], hdg_range[1], size=N)
    particles[:, 2] %= 2 * np.pi
    return particles

def create_gaussian_particles(mean, std, N):
    particles = np.empty((N, 3))
    particles[:, 0] = mean[0] + (randn(N) * std[0])
    particles[:, 1] = mean[1] + (randn(N) * std[1])
    particles[:, 2] = mean[2] + (randn(N) * std[2])
    particles[:, 2] %= 2 * np.pi
    return particles

def predict(particles, u, std, dt=1.):
    """ move according to control input u (heading change, velocity)
    with noise Q (std heading change, std velocity)`"""

    N = len(particles)
    # update heading
    particles[:, 2] += u[0] + (randn(N) * std[0])
    particles[:, 2] %= 2 * np.pi

    # move in the (noisy) commanded direction
    dist = (u[1] * dt) + (randn(N) * std[1])
    particles[:, 0] += np.cos(particles[:, 2]) * dist
    particles[:, 1] += np.sin(particles[:, 2]) * dist

    


def update(particles, weights, z, R, landmarks):
    weights.fill(1.)
    for i, landmark in enumerate(landmarks):
        distance = np.linalg.norm(particles[:, 0:2] - landmark, axis=1)
        weights *= scipy.stats.norm(distance, R).pdf(z[i])

    weights += 1.e-300      # avoid round-off to zero
    weights /= sum(weights) # normalize

def estimate(particles, weights):
    """returns mean and variance of the weighted particles"""

    pos = particles[:, 0:2]
    mean = np.average(pos, weights=weights, axis=0)
    var  = np.average((pos - mean)**2, weights=weights, axis=0)
    return mean, var




def particle_filter(ser):
    return    
'''