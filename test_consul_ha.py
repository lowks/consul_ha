import unittest
import json
import urllib2
import time

from consulHa import ConsulHa

class StateHandler:
    def __init__(self, responses):
        self
        self.responses = responses

    def is_leader(self):
        try:
            self.called_is_leader = True
            return self.responses['is_leader']
        except KeyError:
            raise Exception("Tried to run unconfigured is_leader")

    def passes_health_requirements(self, members_array):
        try:
            self.called_passes_health_requirements = True
            return self.responses['passes_health_requirements']
        except KeyError:
            raise Exception("Tried to run unconfigured passes_health_requirements")

    def promote(self):
        try:
            self.called_promote = True
            return self.responses['promote']
        except KeyError:
            raise Exception("Tried to run unconfigured promote")

    def demote(self, leader):
        try:
            self.called_demote = True
            return self.responses['demote']
        except KeyError:
            raise Exception("Tried to run unconfigured demote")

    def follow_the_leader(self, leader):
        try:
            self.called_follow_the_leader = True
            return self.responses['follow_the_leader']
        except KeyError:
            raise Exception("Tried to run unconfigured follow_the_leader")

def grab_session_for_service(service):
    session_data = {
            "Name": "%s-%s" % (time.gmtime(0), service),
            "LockDelay": "0s",
            "Checks": []
            }

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request('http://localhost:8500/v1/session/create', data=json.dumps(session_data))
    request.get_method = lambda: 'PUT'
    session_response = opener.open(request).read()
    session_id = json.loads(session_response)["ID"]

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request('http://localhost:8500/v1/kv/service/%s/leader?acquire=%s' % (service, session_id), data="%s" % time.gmtime(0))
    request.get_method = lambda: 'PUT'
    opener.open(request)

class ConsuleHaTest(unittest.TestCase):
    def setUp(self):
        self.clearConsulSessions()

    def clearConsulSessions(self):
        for session in json.loads(urllib2.urlopen("http://localhost:8500/v1/session/list").read()):
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request('http://localhost:8500/v1/session/destroy/%s' % session["ID"])
            request.get_method = lambda: 'PUT'
            opener.open(request)

    def test_obtain_lock_as_primary(self):
        consul_ha = ConsulHa("healthy-primary", 0)
        state_handler = StateHandler({'is_leader': True})
        consul_ha.state_handler = state_handler

        consul_ha.run_cycle()

        self.assertTrue(state_handler.called_is_leader)
        pass

    def test_obtain_lock_as_secondary_and_most_healthy(self):
        consul_ha = ConsulHa("healthy-secondary", 0)
        state_handler = StateHandler({'is_leader': False, 'passes_health_requirements': True, 'promote': True, 'follow_the_leader': True})
        consul_ha.state_handler = state_handler

        consul_ha.run_cycle()

        self.assertTrue(state_handler.called_is_leader)
        self.assertTrue(state_handler.called_passes_health_requirements)
        self.assertTrue(state_handler.called_promote)
        pass

    def test_fails_to_create_session_id_when_unhealthy(self):
        consul_ha = ConsulHa("unhealthy-secondary", 0)
        state_handler = StateHandler({})
        consul_ha.state_handler = state_handler

        self.assertFalse(consul_ha.run_cycle())
        pass

    def test_obtain_lock_as_secondary_and_not_most_healthy(self):
        consul_ha = ConsulHa("healthy-secondary", 0)
        state_handler = StateHandler({'is_leader': False, 'passes_health_requirements': False})
        consul_ha.state_handler = state_handler

        consul_ha.run_cycle()

        self.assertTrue(state_handler.called_is_leader)
        self.assertTrue(state_handler.called_passes_health_requirements)
        pass

    def test_lose_lock_as_primary_with_new_primary(self):
        grab_session_for_service('healthy-primary')

        consul_ha = ConsulHa("healthy-primary", 0)
        state_handler = StateHandler({'is_leader': True, 'demote': True})
        consul_ha.state_handler = state_handler

        consul_ha.run_cycle()

        self.assertTrue(state_handler.called_is_leader)
        self.assertTrue(state_handler.called_demote)

        pass

if __name__ == '__main__':
    unittest.main()
