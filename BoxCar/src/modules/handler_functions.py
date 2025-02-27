from classes.simulation import Simulation
import numpy as np
from classes.rider import Rider
from classes.driver import Driver
import time
import matplotlib.pyplot as plt

def execute_rider_join(sim:Simulation, rider:Rider):
    if sim.plot:
        point = sim.ax.scatter(*rider.origin, c='r')
        sim.rider_points[rider] = {'join': point}
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
    
    if sim.unmatched_drivers:
        # calculate and enumerate the distances to drivers
        distances = [(i, np.linalg.norm(driver.position - rider.origin)) for (i, driver) in enumerate(sim.unmatched_drivers)]
        # find the minimum unmatched driver (search over index 1, then take index 0 for driver's index in unmatched_drivers)
        trip_distance = np.linalg.norm(rider.origin - rider.destination)
        trip_profit = Driver.earnings_per_mile * trip_distance + Driver.initial_fare

        driver_distance = min(distances, key=lambda x: x[1])
        trip_cost = Driver.costs_per_mile * driver_distance[1] + Driver.costs_per_mile * trip_distance
        if trip_profit - trip_cost < 0:
            sim.unmatched_riders.append(rider)
            sim.add_event(rider.abandonment_time, "rider abandon", [rider])
        else:
            closest_driver_index = driver_distance[0]
            driver = sim.unmatched_drivers[closest_driver_index]
            sim.add_event(sim.current_time, "ride accept", [rider, driver])
    else:
        # if no drivers are immediately available, add the rider to the unmatched list, and schedule their abandon time
        sim.unmatched_riders.append(rider)
        sim.add_event(rider.abandonment_time, "rider abandon", [rider])
        
    # schedule the next rider's arrival
    next_rider_arrival_time = sim.current_time + sim.distributions["rider inter-arrival"]()
    sim.add_event(next_rider_arrival_time, "rider join", [Rider(sim, next_rider_arrival_time)])

def execute_rider_abandon(sim:Simulation, rider:Rider):
    # if the rider has been assigned, they cannot abandon. This should not happen
    if rider.assigned:
        print("\033[A", "Rider assigned, cannot abandon\n\n\n\n\n")
        sim.ax.scatter(*rider.origin, c='orange', zorder=10)
        time.sleep(100)
        return
    
    # change the color of the point at the rider's origin to indicate abandonment
    if sim.plot:
        sim.rider_points[rider]['join'].remove()
        point = sim.ax.scatter(*rider.origin, c='lightgray')
        del sim.rider_points[rider]['join']
        sim.rider_points[rider] = {'abandon': point, 'time': sim.current_time}
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
    
    # if statement not strictly necessary as only riders in unmatched_riders can abandon
    if rider in sim.unmatched_riders:
        sim.unmatched_riders.remove(rider)

def execute_driver_join(sim:Simulation, driver:Driver):
    if sim.plot:
        point = sim.ax.scatter(*driver.position, c='b')
        sim.driver_points[driver] = {'position': point}
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
    
    if sim.unmatched_riders:
        # calculate and enumerate the distances to riders
        distances = [(i, np.linalg.norm(rider.origin - driver.position)) for (i, rider) in enumerate(sim.unmatched_riders)]
        # find the minimum unmatched rider (search over index 1, then take index 0 for rider's index in unmatched_riders)
        closest_rider_index = min(distances, key=lambda x: x[1])[0]
        rider = sim.unmatched_riders[closest_rider_index]
        
        sim.add_event(sim.current_time, "ride accept", [rider, driver])
    else:
        # if no riders are immediately available, add the driver to the unmatched list
        driver.idle_start_time = sim.current_time
        sim.unmatched_drivers.append(driver)
    
    # schedule the driver's leave time
    sim.add_event(driver.leave_time, "driver leave", [driver])
    
    # schedule the next driver's arrival
    next_driver_arrival_time = sim.current_time + sim.distributions["driver inter-arrival"]()
    sim.add_event(next_driver_arrival_time, "driver join", [Driver(sim, next_driver_arrival_time)])

def execute_driver_leave(sim:Simulation, driver:Driver):
    # change the color of the point at the driver's position to indicate leaving
    if sim.plot:
        sim.driver_points[driver]['position'].remove()
        point = sim.ax.scatter(*driver.position, c='k')
        sim.driver_points[driver]['position'] = point
        sim.driver_points[driver]['time'] = sim.current_time
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
    
    # first handle the case where the driver still has a passenger. In this case, we schedule the dropoff event
    if driver.status == Driver.busy:
        sim.add_event(driver.dropoff_time, "driver leave", [driver])
        sim.event_counters["driver leave"] -= 1
        driver.idle_start_time = driver.dropoff_time
        driver.status = Driver.leaving
        
    # next handle the case where the driver is idle, or was planning to leave during the last ride
    elif driver.status == Driver.idle or driver.status == Driver.leaving:
        
        driver.status = Driver.left
        driver.total_idle_time += sim.current_time - driver.idle_start_time
        
        sim.driver_total_idle_times.append(driver.total_idle_time)
        sim.driver_total_times.append(driver.available_length)
        sim.driver_total_idle_percentages.append(driver.total_idle_time / driver.available_length)
        
        sim.driver_total_rides.append(driver.total_rides)
        sim.driver_total_earnings.append(driver.total_earnings)
        sim.driver_total_costs.append(driver.total_costs)
        sim.driver_total_profit.append(driver.total_earnings - driver.total_costs)
        sim.driver_total_distance.append(driver.total_distance)
        
        if driver in sim.unmatched_drivers:
            sim.unmatched_drivers.remove(driver)

def execute_ride_accept(sim:Simulation, rider:Rider, driver:Driver):
    if sim.plot:
        # plot lines between points
        line1 = plt.Line2D([driver.position[0], rider.origin[0]], [driver.position[1], rider.origin[1]], c='pink', linewidth=0.5, zorder=1)
        line2 = plt.Line2D([rider.origin[0], rider.destination[0]], [rider.origin[1], rider.destination[1]], c='pink', linestyle='dotted', linewidth=0.5, zorder=1)
        
        # add to lines list and plot
        sim.lines[driver] = {'leg1': line1, 'leg2': line2}
        sim.ax.add_line(line1)
        sim.ax.add_line(line2)
        
        # plot points
        sim.driver_points[driver]['position'].remove()
        sim.rider_points[rider]['join'].remove()
        driver_position_point = sim.ax.scatter(*driver.position , c='lightblue', zorder=2)
        driver_pickup_point = sim.ax.scatter(*rider.origin, c='pink', zorder=2)
        driver_destination_point = sim.ax.scatter(*rider.destination, c='pink', marker='x', zorder=2)
        sim.driver_points[driver] = {'position': driver_position_point, 'pickup': driver_pickup_point, 'destination': driver_destination_point}
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
    
    # remove both the rider and driver from the unmatched lists
    if rider in sim.unmatched_riders:
        sim.unmatched_riders.remove(rider)
    if driver in sim.unmatched_drivers:
        driver.total_idle_time += sim.current_time - driver.idle_start_time
        sim.driver_single_idle_times.append(sim.current_time - driver.idle_start_time)
        sim.unmatched_drivers.remove(driver)
        
    # we now remove the event for the rider abandon
    abandon_index = next((i for i, event in enumerate(sim.event_calendar) if event['type'] == "rider abandon" and event['data'][0] is rider), None)
    if abandon_index is not None:
        sim.event_calendar.pop(abandon_index)
        
    # set driver flag to busy and the rider flag to assigned
    driver.status = Driver.busy
    
    rider.assigned = True
    rider.assignment_time = sim.current_time - rider.join_time
    sim.rider_wait_time_assignments.append(rider.assignment_time)
    
    # calculate the distance between the drivers position and the rider's origin
    first_leg_distance = np.linalg.norm(driver.position - rider.origin)
    # calculate the time to reach the rider
    first_leg_time = sim.distributions["actual trip time"](first_leg_distance)
    
    # calculate the distance between the rider's origin and destination
    second_leg_distance = np.linalg.norm(rider.origin - rider.destination)
    # calculate the time to reach the destination
    second_leg_time = sim.distributions["actual trip time"](second_leg_distance)
    
    # Calculate and add the total earnings for the driver
    driver.this_ride_earnings += Driver.initial_fare 
    driver.this_ride_earnings += (Driver.earnings_per_mile * second_leg_distance) # only counts from pickup to dropoff
    # Calculate and add the total distance for the driver
    driver.this_ride_costs += Driver.costs_per_mile * (first_leg_distance + second_leg_distance)
    
    # store the distances for later use
    driver.this_ride_first_leg_distance = first_leg_distance
    driver.this_ride_second_leg_distance = second_leg_distance
    
    sim.driver_single_trip_distances.append(first_leg_distance + second_leg_distance)
    sim.driver_single_trip_times.append(first_leg_time + second_leg_time)
    
    rider.second_leg_time = second_leg_time
    sim.rider_pickup_to_drive_ratios.append(first_leg_time / second_leg_time)
        
    # schedule the pickup and dropoff events, and record times in the driver object
    driver.pickup_time = sim.current_time + first_leg_time
    driver.dropoff_time = driver.pickup_time + second_leg_time
    sim.add_event(driver.pickup_time, "ride pickup", [rider, driver])
    sim.add_event(driver.dropoff_time, "ride completion", [rider, driver])    
    

def execute_ride_pickup(sim:Simulation, rider:Rider, driver:Driver):
    if sim.plot:
        # remove the current lines
        if driver in sim.lines:
            sim.lines[driver]['leg1'].remove()
            sim.lines[driver]['leg2'].remove()
            del sim.lines[driver]['leg1']
            
        # plot the second leg of the trip using a solid line
        line2 = plt.Line2D([rider.origin[0], rider.destination[0]], [rider.origin[1], rider.destination[1]], c='pink', linewidth=0.5, zorder=1)
        sim.ax.add_line(line2)
        sim.lines[driver] = {'leg2': line2}
        
        # move markers
        sim.driver_points[driver]['position'].remove()
        sim.driver_points[driver]['pickup'].remove()
        col = 'black' if driver.status == Driver.leaving else 'lightblue'
        driver_pickup = sim.ax.scatter(rider.origin[0], rider.origin[1], c=col, zorder=2)
        sim.driver_points[driver]['position'] = driver_pickup
        del sim.driver_points[driver]['pickup']
        
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
    
    driver.position = rider.origin
    driver.total_distance += driver.this_ride_first_leg_distance
    
    rider.picked_up = True
    rider.pickup_time = sim.current_time - rider.join_time
    
    sim.rider_wait_time_pickups.append(rider.pickup_time)
    

def execute_ride_completion(sim:Simulation, rider:Rider, driver:Driver):
    if sim.plot:
        if driver in sim.lines:
            sim.lines[driver]['leg2'].remove()
            del sim.lines[driver]['leg2']
        
        sim.driver_points[driver]['position'].remove()
        sim.driver_points[driver]['destination'].remove()
        new_position = sim.ax.scatter(*rider.destination, c='blue', zorder=2)
        sim.driver_points[driver]['position'] = new_position
        del sim.driver_points[driver]['destination']
        
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()

    driver.status=Driver.idle
    driver.position = rider.destination
    
    driver.total_distance += driver.this_ride_second_leg_distance
    driver.total_earnings += driver.this_ride_earnings
    driver.total_costs += driver.this_ride_costs
    
    sim.driver_single_trip_earnings.append(driver.this_ride_earnings)
    sim.driver_single_trip_costs.append(driver.this_ride_costs)
    sim.driver_single_trip_profit.append(driver.this_ride_earnings - driver.this_ride_costs)
    
    sim.rider_wait_time_dropoffs.append(sim.current_time - rider.join_time)
    sim.rider_direct_time_to_dropoffs.append(rider.second_leg_time)
    
    #reset the driver's earnings and costs for the next ride
    driver.this_ride_earnings = 0
    driver.this_ride_costs = 0
    driver.total_rides += 1
    
    driver.idle_start_time = sim.current_time
    
    
    # if the driver should have left, we do not consider any further rides. The next event has already been scheduled to be the drivers leave event
    if sim.current_time > driver.leave_time:
        return
    # otherwise, we try to assign the driver to a new rider
    elif sim.unmatched_riders:
        # calculate and enumerate the distances to riders
        distances = [(i, np.linalg.norm(rider.origin - driver.position)) for (i, rider) in enumerate(sim.unmatched_riders)]
        # find the minimum unmatched rider (search over index 1, then take index 0 for rider's index in unmatched_riders)
        
        closest_rider = min(distances, key=lambda x: x[1])
        closest_rider_index = closest_rider[0]
        closest_rider_distance = closest_rider[1]

        rider = sim.unmatched_riders[closest_rider_index]
        trip_distance = np.linalg.norm(rider.origin - rider.destination)
        trip_profit = Driver.earnings_per_mile * trip_distance + Driver.initial_fare
        trip_cost = Driver.costs_per_mile * (closest_rider_distance + trip_distance)

        if trip_profit - trip_cost < 0:
            sim.unmatched_drivers.append(driver)
        else:
            sim.add_event(sim.current_time, "ride accept", [rider, driver])
    # and failing that, we add the driver to the unmatched list
    else:
        # if no riders are immediately available, add the driver to the unmatched list
        sim.unmatched_drivers.append(driver)
        
            
    #TODO: Add ride completion statistics

def execute_termination(sim:Simulation):
    if sim.plot:
        sim.ax.spines['top'].set_color('red')
        sim.ax.spines['bottom'].set_color('red')
        sim.ax.spines['left'].set_color('red')
        sim.ax.spines['right'].set_color('red')
        sim.fig.canvas.draw()
        sim.fig.canvas.flush_events()
        plt.ioff()
    
    pass
    
        
        
        
    