# consul-ha

This library simplifies the requirements for building high availabilty
coordination using [https://www.consul.io/](Consul).  It will manage the
key and state, while allowing you to define functions for promotion,
demotion, and health checks.

# Usage

This package is intended to run as a process along side each consul
server.  Therefore, you should have a 1-1 ratio of consul server to
process running this.

First, define your functions for health checks:

```python
def promote():
  print "Take the action to promote this member."

def demote(leader_ip):
  print "Triggered by an event emitted from consul."
  print "Take the action to follow the new leader."

def is_leader:
  return false;

def follow_the_leader(leader_ip):
  print "Ensure following the proper leader."
```

Then, supply your functions to the `consul.run` method:

```python
import consulHA

consulHA.run(promote, demote, is_leader, follow_the_leader)
```
