# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations

known_drivers = {
    'dummy': 'libra.mgm.controllers.vip.drivers.dummy.driver',
    'floating': 'libra.mgm.controllers.vip.drivers.floating.driver',
    'fixed': 'libra.mgm.controllers.vip.drivers.fixed.driver'
}


class BuildIpDriver(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()


class AssignIpDriver(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def check_ip(self, ip, port):
        raise NotImplementedError()


class RemoveIpDriver(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()


class DeleteIpDriver(object):

    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, msg):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()
