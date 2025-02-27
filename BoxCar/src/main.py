
from classes.simulation import Simulation
# from classes.generate_random import Distributions
from classes.generate_random_alternative import Distributions
from classes.event_handlers import EventHandlers



def main():
    handlers = EventHandlers(None)
    distributions = Distributions(None)
    
    sim = Simulation(handlers, distributions)
    
    handlers.simulation = sim
    distributions.simulation = sim
    
    sim.run()
    
    
    
if __name__ == "__main__":
    main()
