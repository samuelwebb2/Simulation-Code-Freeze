import random
import numpy as np
import numpy.typing as npt
import scipy.stats as stats

class Distributions:
    def __init__(self, simulation):
        self.simulation = simulation
        
    def generate_driver_inter_arrival(self)->float:
        return random.expovariate(4.09/60)
    
    def generate_driver_available_length(self)->float:
        return 60 * random.uniform(5, 8)
    
    def generate_driver_initial_coordinates(self)->npt.ArrayLike:
        x = stats.skewnorm.rvs(a=-0.66, loc=11.77, scale=4.77)
        y = stats.skewnorm.rvs(a=-1.86, loc=15.74, scale=6.13)
        return np.array([x, y])
    
    def generate_rider_origin_coordinates(self)->npt.ArrayLike:
        x = stats.skewnorm.rvs(a=11.70, loc=0.55, scale=6.89)
        y = stats.lognorm.rvs(s=0.16, loc=-19.07, scale=26.89)
        return np.array([x, y])
    
    def generate_rider_destination_coordinates(self)->npt.ArrayLike:
        x = stats.lognorm.rvs(s=0.08, loc=-51.78, scale=60.91)
        y = stats.skewnorm.rvs(a=-1.73, loc=15.70, scale=6.24)
        return np.array([x, y])
    
    def generate_coordinates(self)->npt.ArrayLike:
        x = random.uniform(0, 20)
        y = random.uniform(0, 20)
        return np.array([x, y])
    
    def generate_rider_inter_arrival(self)->float:
        return random.expovariate(32.01/60)
    
    def generate_rider_patience(self)->float:
        return random.expovariate(5/60)
    
    def generate_actual_trip_time(self, distance)->float:
        average_speed = 20
        expected_trip_time = distance / average_speed
        actual_trip_time = 60 * random.uniform(0.8 * expected_trip_time, 1.2 * expected_trip_time)
        return actual_trip_time