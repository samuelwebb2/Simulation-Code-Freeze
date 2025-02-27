import numpy as np
import numpy.typing as npt
from numpy.random import uniform
import classes.simulation as simulation

class Rider:
    
    def __init__(self, sim_instance:simulation, join_time:float):
        self.origin:npt.ArrayLike = sim_instance.distributions["rider origin coordinates"]()
        self.destination:npt.ArrayLike = sim_instance.distributions["rider destination coordinates"]()
        
        patience:float = sim_instance.distributions["rider patience"]()
        self.abandonment_time:float = join_time + patience
        
        self.assigned:bool = False
        self.picked_up:bool = False
        
        self.join_time:float = join_time
        self.assignment_time:float = np.inf
        self.pickup_time:float = np.inf
        
        self.second_leg_time:float = np.inf
        
