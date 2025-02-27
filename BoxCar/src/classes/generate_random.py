import random
import numpy as np
import numpy.typing as npt

class Distributions:
    def __init__(self, simulation):
        self.simulation = simulation
    
    def generate_driver_inter_arrival(self)->float:
        return random.expovariate(3/60)
    
    def generate_driver_available_length(self)->float:
        return 60 * random.uniform(5, 8)
    
    def generate_driver_initial_coordinates(self)->npt.ArrayLike:
        x = random.uniform(0, 20)
        y = random.uniform(0, 20)
        return np.array([x, y])
    
    def generate_rider_origin_coordinates(self)->npt.ArrayLike:
        x = random.uniform(0, 20)
        y = random.uniform(0, 20)
        return np.array([x, y])
    
    def generate_rider_destination_coordinates(self)->npt.ArrayLike:
        x = random.uniform(0, 20)
        y = random.uniform(0, 20)
        return np.array([x, y])
    
    def generate_coordinates(self)->npt.ArrayLike:
        x = random.uniform(0, 20)
        y = random.uniform(0, 20)
        return np.array([x, y])
    
    def generate_rider_inter_arrival(self)->float:
        return random.expovariate(30/60)
    
    def generate_rider_patience(self)->float:
        return random.expovariate(5/60)
    
    def generate_actual_trip_time(self, distance)->float:
        average_speed = 20
        expected_trip_time = distance / average_speed
        actual_trip_time = 60 * random.uniform(0.8 * expected_trip_time, 1.2 * expected_trip_time)
        return actual_trip_time