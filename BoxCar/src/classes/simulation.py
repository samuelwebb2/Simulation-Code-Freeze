from typing import Callable, List, Dict, Any
from bisect import bisect_right
from classes.rider import Rider
from classes.driver import Driver
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy.typing as npt
import numpy as np
from tabulate import tabulate
import csv
import os



print("simulation.py loaded successfully")

class Simulation:
    def __init__(self, handlers, distributions: Any = None):
        
        self.plot:bool = False
        if self.plot:
            plt.ion()
            self.fig, self.ax = plt.subplots()
            self.ax.set_xlim(0, 20)
            self.ax.set_ylim(0, 20)
            self.lines: Dict[Driver, Dict[str, plt.Line2D]] = {}
            self.driver_points: Dict[Driver, Dict[str, npt.ArrayLike]] = {}
            self.rider_points: Dict[Rider, Dict[str, mpl.collections.PathCollection]] = {}
        
        self.simulation_sleep_time = 0
        self.simulation_length = 60 * 8766 # Termination time (minutes)
        self.current_time = 0               # Keep tracks of simulation clock
        
        self.event_calendar: List[Dict[str, Any]] = [] # Event calendar is initialized as empty
        self.distributions: Dict[str, Callable[[Any], None]] = {}
        self.event_handlers: Dict[str, Callable[[Any], None]] = {} # The event_handlers list will associate each event with the modules/functions necessary to execute that event. This list is empty and designed to be dynamic to flexibility add or remove event types.
        self.unmatched_riders: List[Rider] = []
        self.unmatched_drivers: List[Driver] = []
        
        # metrics to ensure that the distributions are correct
        self.event_counters: Dict[str, int] = {}
        
        # KPIs - riders
        self.rider_wait_time_assignments = []
        self.rider_wait_time_pickups = []
        self.rider_wait_time_dropoffs = []
        self.rider_direct_time_to_dropoffs = []
        self.rider_pickup_to_drive_ratios = []
        
        self.driver_total_rides = []
        
        self.driver_total_idle_times = []
        self.driver_single_idle_times = []
        self.driver_total_idle_percentages = []
        
        self.driver_total_times = []
        self.driver_single_trip_times = []
        
        self.driver_total_distance = []
        self.driver_single_trip_distances = []
        
        self.driver_total_costs = []
        self.driver_single_trip_costs = []
        
        self.driver_total_earnings = []
        self.driver_single_trip_earnings = []
        
        self.driver_total_profit = []
        self.driver_single_trip_profit = []
        
        
        if distributions:
            self.register_distribution("rider inter-arrival", distributions.generate_rider_inter_arrival)
            self.register_distribution("driver inter-arrival", distributions.generate_driver_inter_arrival)
            self.register_distribution("rider patience", distributions.generate_rider_patience)
            self.register_distribution("driver available length", distributions.generate_driver_available_length)
            # self.register_distribution("coordinates", distributions.generate_coordinates)
            self.register_distribution("driver initial coordinates", distributions.generate_driver_initial_coordinates)
            self.register_distribution("rider origin coordinates", distributions.generate_rider_origin_coordinates)
            self.register_distribution("rider destination coordinates", distributions.generate_rider_destination_coordinates)
            self.register_distribution("actual trip time", distributions.generate_actual_trip_time)
        
        if handlers:
            self.register_event_handler("rider join", handlers.handle_rider_join)
            self.register_event_handler("rider abandon", handlers.handle_rider_abandon)
            self.register_event_handler("driver join", handlers.handle_driver_join)
            self.register_event_handler("driver leave", handlers.handle_driver_leave)
            self.register_event_handler("ride accept", handlers.handle_ride_accept)
            self.register_event_handler("ride pickup", handlers.handle_ride_pickup)
            self.register_event_handler("ride completion", handlers.handle_ride_completion)
            self.register_event_handler("termination", handlers.handle_termination)
        
        first_rider_join_time = self.current_time + self.distributions["rider inter-arrival"]()
        first_rider = Rider(self, first_rider_join_time)
        first_driver_join_time = self.current_time + self.distributions["driver inter-arrival"]()
        first_driver = Driver(self, first_driver_join_time)
        self.add_event(first_rider_join_time, "rider join", [first_rider])
        self.add_event(first_driver_join_time, "driver join", [first_driver])
        self.add_event(self.simulation_length, "termination", None)
        
        
    def add_event(self, event_time:float, event_type: str, event_data: Any = None)->None:
        event = {'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self.event_calendar], event_time)
        self.event_calendar.insert(index, event)
        
    def register_distribution(self, random_quantity: str, handler: Callable[[Any], None]):
        self.distributions[random_quantity] = handler
        
        
    def register_event_handler(self, event_type: str, handler: Callable[[Any], None]) -> None:
        # This function allows us to dynamically add event types to the list.
        self.event_handlers[event_type] = handler
        
    def progress_time(self) -> None:
        if not self.event_calendar:
            print("No more events to process.")
            return

        # print important details in event calendar
        # print("\n", [(event['time'], event['type']) for event in self.event_calendar])

        next_event = self.event_calendar.pop(0)
        previous_time = self.current_time
        self.current_time = next_event['time']
        event_type = next_event['type']
        event_data = next_event['data']
        
        # event counter to double check random distribution validity
        self.event_counters[event_type] = self.event_counters.get(event_type, 0) + 1
        #remove oldest abandon point if there are more than 10
        if self.plot:
            min_point = None
            abandoned_points = [rider for rider in self.rider_points.keys() if 'abandon' in self.rider_points[rider]]
            if len(abandoned_points) > 10:
                min_point = min(abandoned_points, key=lambda rider: self.rider_points[rider]['time'])
                        
                self.rider_points[min_point]['abandon'].remove()
                del self.rider_points[min_point]
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()

            min_point = None
            leaving_points = [driver for driver in self.driver_points.keys() if driver.status == Driver.left]
            if len(leaving_points) > 10:
                min_point = min(leaving_points, key=lambda driver: self.driver_points[driver]['time'])
                        
                self.driver_points[min_point]['position'].remove()
                del self.driver_points[min_point]
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
        
        #-----update metrics here-----#
        
        time.sleep(self.simulation_sleep_time)
        # print(f"Processing event @ {self.current_time:.2f}:\t {event_type}")
        # Calculate and display the loading bar
        progress = self.current_time / self.simulation_length
        if int(previous_time / self.simulation_length * 10) < int(progress * 10):
            bar_length = 10
            block = int(round(bar_length * progress))
            loading_bar = "#" * block + "-" * (bar_length - block)
            print(f"\rProgress: [{loading_bar}] {progress * 100:.2f}%", end="")

        if event_type in self.event_handlers:
            self.event_handlers[event_type](event_data)
        else:
            print(f"No handler registered for event type: {event_type}")
            
            
    def run(self) -> None:
        """
        Run the simulation until all events are processed or a 'termination' event is encountered.
        """
        # print(self.event_calendar)
        terminate_sim = 0
        while self.event_calendar:
            next_event = self.event_calendar[0]  # Peek at the next event
            if next_event['type'] == "termination":
                terminate_sim = 1
            self.progress_time()
            if terminate_sim == 1:
                if self.plot: plt.show(block=True)
                
                self.printKPIsTable()
                self.saveToCSV()
                
                break
        if terminate_sim == 0:
            print("No more event to execute!")
            
    def saveToCSV(self):
        output_dir = "BoxCar/output"
        os.makedirs(output_dir, exist_ok=True)

        def save_to_csv(filename, headers, data):
            with open(os.path.join(output_dir, filename), mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(data)

        # Save driver metrics
        save_to_csv("driver_total_idle_times.csv", ["Driver Total Idle Times"], [[time] for time in self.driver_total_idle_times])
        save_to_csv("driver_total_times.csv", ["Driver Total Times"], [[time] for time in self.driver_total_times])
        save_to_csv("driver_idle_percentages.csv", ["Driver Idle Percentages"], [[percentage] for percentage in self.driver_total_idle_percentages])
        save_to_csv("driver_total_rides.csv", ["Driver Total Rides"], [[rides] for rides in self.driver_total_rides])
        save_to_csv("driver_total_distance.csv", ["Driver Total Distance"], [[distance] for distance in self.driver_total_distance])
        save_to_csv("driver_total_costs.csv", ["Driver Total Costs"], [[cost] for cost in self.driver_total_costs])
        save_to_csv("driver_single_trip_costs.csv", ["Driver Single Trip Costs"], [[cost] for cost in self.driver_single_trip_costs])
        save_to_csv("driver_total_earnings.csv", ["Driver Total Earnings"], [[earnings] for earnings in self.driver_total_earnings])
        save_to_csv("driver_single_trip_earnings.csv", ["Driver Single Trip Earnings"], [[earnings] for earnings in self.driver_single_trip_earnings])
        save_to_csv("driver_total_profit.csv", ["Driver Total Profit"], [[profit] for profit in self.driver_total_profit])
        save_to_csv("driver_single_trip_profit.csv", ["Driver Single Trip Profit"], [[profit] for profit in self.driver_single_trip_profit])
        save_to_csv("driver_single_trip_times.csv", ["Driver Single Trip Times"], [[time] for time in self.driver_single_trip_times])
        save_to_csv("driver_single_trip_distances.csv", ["Driver Single Trip Distances"], [[distance] for distance in self.driver_single_trip_distances])
        save_to_csv("driver_single_idle_times.csv", ["Driver Single Idle Times"], [[time] for time in self.driver_single_idle_times])

        # Save rider metrics
        save_to_csv("rider_wait_time_assignments.csv", ["Rider Wait Time Assignments"], [[time] for time in self.rider_wait_time_assignments])
        save_to_csv("rider_wait_time_pickups.csv", ["Rider Wait Time Pickups"], [[time] for time in self.rider_wait_time_pickups])
        save_to_csv("rider_wait_time_dropoffs.csv", ["Rider Wait Time Dropoffs"], [[time] for time in self.rider_wait_time_dropoffs])
        save_to_csv("rider_direct_time_to_dropoffs.csv", ["Rider Direct Time To Dropoffs"], [[time] for time in self.rider_direct_time_to_dropoffs])
        save_to_csv("rider_pickup_to_drive_ratios.csv", ["Rider Pickup To Drive Ratios"], [[ratio] for ratio in self.rider_pickup_to_drive_ratios])

    def printKPIsTable(self):
        def five_number_summary(data):
            if not data:
                return [0, 0, 0, 0, 0]
            return [
                np.min(data),
                np.percentile(data, 25),
                np.mean(data),
                np.percentile(data, 75),
                np.max(data)
            ]

        # Prepare data for the rider KPIs table
        headers_rider = ["Metric", "Min", "Q1", "Mean", "Q3", "Max"]
        data_rider = [
            ["Average abandonments per hour", "-", "-", f"{self.event_counters['rider abandon'] / (self.simulation_length / 60):.2f}", "-", "-"],
            ["Rider assignment wait time (minutes)", *map(lambda x: f"{x:.2f}", five_number_summary(self.rider_wait_time_assignments))],
            ["Rider pickup wait time (minutes) (incl. assignment time)", *map(lambda x: f"{x:.2f}", five_number_summary(self.rider_wait_time_pickups))],
            ["Rider dropoff wait time (minutes) (incl. pickup time)", *map(lambda x: f"{x:.2f}", five_number_summary(self.rider_wait_time_dropoffs))],
            ["Time directly to dropoff (minutes) (w/o pickup time)", *map(lambda x: f"{x:.2f}", five_number_summary(self.rider_direct_time_to_dropoffs))],
            ["Rider ratio of pickup to drive time (%)", *map(lambda x: f"{x * 100:.2f}", five_number_summary(self.rider_pickup_to_drive_ratios))]
        ]

        print("\nRider Key Performance Indicators (KPIs):")
        print(tabulate(data_rider, headers=headers_rider, tablefmt="grid"))

        # Prepare data for the driver KPIs table
        headers_driver = ["Metric", "Min", "Q1", "Mean", "Q3", "Max"]
        data_driver = [
            ["Driver idle percentage (%)", *map(lambda x: f"{x * 100:.2f}", five_number_summary(self.driver_total_idle_percentages))],
            ["Equivalent Driver idle time per 5 hour day (minutes)", *map(lambda x: f"{x * 5 * 60:.2f}", five_number_summary(self.driver_total_idle_percentages))],
            ["Equivalent Driver idle time per 8 hour day (minutes)", *map(lambda x: f"{x * 8 * 60:.2f}", five_number_summary(self.driver_total_idle_percentages))],
            ["Number of rides per driver", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_total_rides))],
            ["Distance driven per driver (miles)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_total_distance))],
            ["Earnings per driver (£)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_total_earnings))],
            ["Costs per driver (£)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_total_costs))],
            ["Profit per driver (£)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_total_profit))]
        ]

        print("\nDriver Key Performance Indicators (KPIs):")
        print(tabulate(data_driver, headers=headers_driver, tablefmt="grid"))

        # Prepare data for the single trip KPIs table
        headers_single_trip = ["Metric", "Min", "Q1", "Mean", "Q3", "Max"]
        data_single_trip = [
            ["Single trip earnings (£)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_single_trip_earnings))],
            ["Single trip cost (£)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_single_trip_costs))],
            ["Single trip profit (£)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_single_trip_profit))],
            ["Single trip time (minutes)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_single_trip_times))],
            ["Single trip distance (miles)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_single_trip_distances))],
            ["Single idle time (minutes)", *map(lambda x: f"{x:.2f}", five_number_summary(self.driver_single_idle_times))]
        ]

        print("\nSingle Trip Key Performance Indicators (KPIs):")
        print(tabulate(data_single_trip, headers=headers_single_trip, tablefmt="grid"))
