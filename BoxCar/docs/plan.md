# Code plan

## The key performance indicators (KPIs)

1. The number of rider abandonments
1. Average wait time per rider
1. Average driver earnings per hour
1. Fairness among drivers
1. Sufficient resting time (proportional to hours worked)

## The state variables

### Simulation

#### Related to drivers

1. Distance travelled per driver
1. Number of journeys taken per driver
1. Earnings per driver (from distance and journeys)
1. Inactive time per driver

#### Related to riders

1. Number of rides (sum of journeys per driver)
1. Cumulative wait time of riders (who had rides)
1. Number of abandonments
1. Cumulative wait time of riders (who aborted rides)

### Driver

1. Status (idle, enroute, busy)
1. Clock off time
1. Distance travelled so far
1. Number of journeys so far
1. Current Location
1. Pickup
1. Destination

### Riders

1. Abandonment time
1. Current location
1. Destination
1. Assigned

## The events that change the system state

1. Rider looking for driver
1. Rider giving up waiting for driver
1. Driver accepting ride
1. Driver pickup rider
1. Driver reached destination
1. Driver clock on
1. Driver clock off
1. Termination

## Keep track of the time
