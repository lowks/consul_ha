# consul-ha

This library simplifies the requirements for building high availabilty
coordination using [https://www.consul.io/](Consul).  It will manage the
key and state, while allowing you to define functions for promotion,
demotion, and health checks.

# Usage

This package is intended to run as a process along side each consul
server.  Therefore, you should have a 1-1 ratio of consul server to
process running this.

First, define your state handler for your monitored application or
database:

```python
class DatabaseHandler:
    def __init__(self):
        self

    def is_leader(self):
      // determine if process is the leader
      // returns boolean

    def passes_health_requirements(self, members_array):
      // determine if this member is healthy enough to become primary 
      // returns boolean

    def promote(self):
      // actions taken, which promotes this member to leadership

    def demote(self, leader):
      // actions taken to demote this member from leadership

    def follow_the_leader(self, leader):
      // actions taken to ensure secondary member is following proper leader
```

Then, supply your initialized class to the a ConsulHa class:

```python
from consulHa import ConsulHa

service_name = "my-database"   # must match service name in Consul
demotion_delay_in_seconds = 60 # between 0 and 60 seconds

consul_ha = ConsulHa(service_name, demotion_delay_in_seconds)
consul_ha.state_handler = DatabaseHandler()
consul_ha.run()
```
