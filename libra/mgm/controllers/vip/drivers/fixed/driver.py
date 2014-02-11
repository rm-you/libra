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
# under the License.

import libra.mgm.controllers.vip.drivers.base as IpDriver
import socket
import time
from novaclient import exceptions
from oslo.config import cfg

from libra.mgm.nova import Node
from libra.openstack.common import log


LOG = log.getLogger(__name__)


class BuildIpDriver(IpDriver.BuildIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info("Fixed-IP mode does not require IP creation")
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
        return self.msg


class AssignIpDriver(IpDriver.AssignIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node(admin=True)
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        network_id = cfg.CONF['mgm']['ip_network_id']

        LOG.info(
            "Assigning Fixed IP from network {0} to {1}"
            .format(network_id, self.msg['name'])
        )
        try:
            node_id = nova.get_node(self.msg['name'])
            LOG.info(
                'Node name {0} identified as ID {1}'
                .format(self.msg['name'], node_id)
            )
            #nova.vip_assign(node_id, self.msg['ip'])
            url = '/servers/{0}/action'.format(node_id)
            body = {
                "addFixedIp": {
                    "networkId": network_id
                }
            }
            resp, body = nova.admin_nova.post(url, body=body)
            if resp.status_code != 202:
                raise Exception(
                    'Response code {0}, message {1} when assigning vip'
                    .format(resp.status_code, body)
                )
        except:
            LOG.exception(
                'Error assigning Fixed IP {0} to {1}'
                .format('?', self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

    def check_ip(self, ip, port):
        LOG.error("Cannot run IP/Port check in FixedIP mode")
        return False
        # TCP connect check to see if fixed IP was assigned correctly
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
                        "TCP connect error after fixed IP assign {0}"
                        .format(ip)
                    )
                    raise
                time.sleep(2)


class RemoveIpDriver(IpDriver.RemoveIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node(admin=True)
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Removing Fixed IP {0} from {1}"
            .format(self.msg['ip'], self.msg['name'])
        )
        try:
            node_id = nova.get_node(self.msg['name'])
            #nova.vip_remove(node_id, self.msg['ip'])
            url = '/servers/{0}/action'.format(node_id)
            body = {
                "removeFixedIp": {
                    "address": msg['ip']
                }
            }
            resp, body = nova.admin_nova.post(url, body=body)
        except:
            LOG.exception(
                'Error removing Fixed IP {0} from {1}'
                .format(self.msg['ip'], self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class DeleteIpDriver(IpDriver.DeleteIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        LOG.info("Fixed-IP mode does not require IP deletion")
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
        return self.msg