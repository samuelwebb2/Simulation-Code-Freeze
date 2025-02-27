import numpy as np
import numpy.typing as npt
from numpy.random import uniform
import classes.simulation as simulation

class Driver:
    
    busy = "busy"
    idle = "idle"
    leaving = "leaving"
    left = "left"
    
    initial_fare = 3
    earnings_per_mile = 2
    costs_per_mile = 0.2
    
    
    def __init__(self, sim_instance:simulation, join_time:float)->None:
        self.available_length:float = sim_instance.distributions["driver available length"]()
        self.leave_time:float = join_time + self.available_length
        
        self.position:npt.ArrayLike = sim_instance.distributions["driver initial coordinates"]()
        self.pickup:npt.ArrayLike = self.position
        self.destination:npt.ArrayLike = self.position
        
        self.pickup_time:float = 0
        self.dropoff_time:float = 0
        
        self.this_ride_first_leg_distance:float = 0 
        self.this_ride_second_leg_distance:float = 0 
        self.total_distance:float = 0
        
        self.total_rides:float = 0
        
        self.total_earnings:float = 0
        self.this_ride_earnings:float = 0
        self.total_costs:float = 0
        self.this_ride_costs:float = 0
        
        self.status:str = self.idle
        self.idle_start_time:float = join_time
        self.total_idle_time:float = 0
        
