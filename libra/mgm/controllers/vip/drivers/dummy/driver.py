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

from libra.openstack.common import log

from random import SystemRandom

import libra.mgm.controllers.vip.drivers.base as IpDriver

LOG = log.getLogger(__name__)


class BuildIpDriver(IpDriver.BuildIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Dummy IP build: {0}'.format(self.msg))
        self.msg['id'] = str(SystemRandom().randint(100000000000,999999999999))
        self.msg['ip'] = "10.0.0.1"
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

class AssignIpDriver(IpDriver.AssignIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Dummy IP assign: {0}'.format(self.msg))
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

    def check_ip(self, ip, port):
        LOG.info('Dummy check_ip: {0}:{1}'.format(ip, port))
        return True

class RemoveIpDriver(IpDriver.RemoveIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Dummy IP remove: {0}'.format(self.msg))
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

class DeleteIpDriver(IpDriver.DeleteIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Dummy IP delete: {0}'.format(self.msg))
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg
