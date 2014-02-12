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

import libra.mgm.controllers.vip.drivers.base as IpDriver
import socket
import time
import random
from oslo.config import cfg

from libra.mgm.nova import Node
from libra.openstack.common import log

LOG = log.getLogger(__name__)


class BuildIpDriver(IpDriver.BuildIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Existing IP build: {0}'.format(self.msg))
        rand_id = "{0}-{1}".format(
            int(time.time()), random.randint(1000000, 9999999)
        )
        self.msg['id'] = rand_id
        self.msg['ip'] = "0.0.0.0"
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class AssignIpDriver(IpDriver.AssignIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Existing IP assign: {0}'.format(self.msg))
        try:
            nova = Node(admin=True)
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        try:
            node_id = nova.get_node(self.msg['name'])
            LOG.info(
                'Node name {0} identified as ID {1}'
                .format(self.msg['name'], node_id)
            )
            server = nova.status(node_id)
            LOG.debug(server)
            vips = server[1]['server']['addresses']
            LOG.debug(vips)
            vip = [x for x in vips['public'] if x['version'] == 4]
            LOG.debug(vip)
            self.msg['ip'] = vip[0]
        except:
            LOG.debug(
                "Assigning Existing IP failed, no IP found for device {0}"
                .format(self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        try:
            if cfg.CONF['mgm']['tcp_check_port']:
                self.check_ip(self.msg['ip'],
                              cfg.CONF['mgm']['tcp_check_port'])
        except:
            LOG.debug(
                "IP Check of Existing IP failed for device {0}"
                .format(self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.debug(
            "Assigned Existing IP {0} to device {1}"
            .format(self.msg['ip'], self.msg['name'])
        )
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

    def check_ip(self, ip, port):
        # TCP connect check to see if floating IP was assigned correctly
        loop_count = 0
        while True:
            try:
                sock = socket.socket()
                sock.settimeout(5)
                sock.connect((ip, port))
                sock.close()
                return True
            except socket.error:
                try:
                    sock.close()
                except:
                    pass
                loop_count += 1
                if loop_count >= 5:
                    LOG.error(
                        "TCP connect error after floating IP assign {0}"
                        .format(ip)
                    )
                    raise
                time.sleep(2)


class RemoveIpDriver(IpDriver.RemoveIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Existing IP remove: {0}'.format(self.msg))
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class DeleteIpDriver(IpDriver.DeleteIpDriver):
    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info('Existing IP delete: {0}'.format(self.msg))
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg
