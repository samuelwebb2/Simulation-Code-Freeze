from typing import Any
import modules.handler_functions as hf

class EventHandlers:
    def __init__(self, simulation):
        self.simulation = simulation
        
    def handle_rider_join(self, event_data: Any):
        hf.execute_rider_join(self.simulation, event_data[0])
        
    def handle_rider_abandon(self, event_data: Any):
        hf.execute_rider_abandon(self.simulation, event_data[0])
        
    def handle_driver_join(self, event_data: Any):
        hf.execute_driver_join(self.simulation, event_data[0])
        
    def handle_driver_leave(self, event_data: Any):
        hf.execute_driver_leave(self.simulation, event_data[0])
        
    def handle_ride_accept(self, event_data: Any):
        hf.execute_ride_accept(self.simulation, event_data[0], event_data[1])
        
    def handle_ride_pickup(self, event_data: Any):
        hf.execute_ride_pickup(self.simulation, event_data[0], event_data[1])
        
    def handle_ride_completion(self, event_data: Any):
        hf.execute_ride_completion(self.simulation, event_data[0], event_data[1])
        
    def handle_termination(self, event_data: Any):
        hf.execute_termination(self.simulation)
        

        
        