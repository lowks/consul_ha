import json
import urllib2
import socket
import sys

class ConsulHa:
    def __init__(self, service_name, lock_delay):
        self.service_name = service_name
        self.hostname = socket.gethostname()
        self.lock_delay = lock_delay
        self.session_id = None

    def init_consul_session(self):
        session_list = json.loads(urllib2.urlopen("http://localhost:8500/v1/session/list").read())
        session_name = "%s-%s" % (self.hostname, self.service_name)

        for session_hash in session_list:
            if session_hash["Name"] == session_name:
                return session_hash["ID"]

        session_data = {
                "Name": session_name,
                "LockDelay": "%ss" % self.lock_delay,
                "Checks": [
                    "serfHealth",
                    "service:%s" % self.service_name
                    ]
                }

        try:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request('http://localhost:8500/v1/session/create', data=json.dumps(session_data))
            request.get_method = lambda: 'PUT'
            session_response = opener.open(request).read()

            return json.loads(session_response)["ID"]
        except urllib2.HTTPError as e:
            print("WARNING: cannot create session until check is healthy: %s" % e)

    def acquire_session_lock(self):
        try:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request('http://localhost:8500/v1/kv/service/%s/leader?acquire=%s' % (self.service_name, self.session_id), data=self.hostname)
            request.get_method = lambda: 'PUT'
            return opener.open(request).read() == "true"
        except urllib2.HTTPError as e:
            print("WARNING: error connecting with consul: %s" % e)

    def fetch_current_leader(self):
        urllib2.urlopen("http://localhost:8500/v1/session/list").read()

    def fetch_members_list(self):
        return json.loads(urllib2.urlopen("http://localhost:8500/v1/health/service/%s" % self.service_name).read())

    def run_cycle(self):
        self.session_id = self.session_id or self.init_consul_session()

        if self.session_id == None:
            return False

        if self.acquire_session_lock():
            if self.state_handler.is_leader():
                return True

            if self.state_handler.passes_health_requirements(self.fetch_members_list()):
                self.state_handler.promote()
                return True
        else:
            if self.state_handler.is_leader():
                self.state_handler.demote(self.fetch_current_leader())
                return True

            self.state_handler.follow_the_leader(self.fetch_current_leader())

    def run(self):
        while True:
            self.run_cycle
            time.sleep(10)
