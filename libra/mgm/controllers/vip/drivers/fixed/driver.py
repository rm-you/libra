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
import random
from oslo.config import cfg

from libra.mgm.nova import Node
from libra.openstack.common import log

LOG = log.getLogger(__name__)


class BuildIpDriver(IpDriver.BuildIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        #LOG.info("Fixed-IP mode does not require IP creation")
        #self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
        rand_id = "{0}-{1}".format(
            int(time.time()), random.randint(1000000, 9999999)
        )
        LOG.info("Fixed IP placeholder {0} created".format(rand_id))
        self.msg['id'] = rand_id
        self.msg['ip'] = "0.0.0.0"
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
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
            #get existing VIPs
            server = nova.status(node_id)
            vips_before = server[1]['server']['addresses']
            vips_before_count = self._count_vips(vips_before)

            #assign a new VIP
            info = {"networkId": network_id}
            nova.action(node_id, "addFixedIp", info, admin=True)

            #get updated VIPs
            ip_in = self.msg['ip']
            for x in range(20):
                server = nova.status(node_id)
                vips_after = server[1]['server']['addresses']
                vips_after_count = self._count_vips(vips_after)
                if vips_after_count > vips_before_count:
                    new_vip = self._new_vip(vips_before, vips_after)
                    self.msg['ip'] = new_vip
                    break
                LOG.info("Didn't find the new Fixed IP, sleeping 3s...")
                time.sleep(3)
            if self.msg['ip'] == ip_in:
                raise Exception('Did not find the new IP address')
            if cfg.CONF['mgm']['tcp_check_port']:
                self.check_ip(self.msg['ip'],
                              cfg.CONF['mgm']['tcp_check_port'])
        except:
            LOG.exception(
                'Error assigning Fixed IP {0} to {1}'
                .format(self.msg['ip'], self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg

    def _count_vips(self, vips):
        count = 0
        for vip_type in vips:
            count += len(vips[vip_type])
        return count

    def _new_vip(self, before, after):
        new_ips = []
        for vip_type in after:
            new_ips += after[vip_type]
        for vip_type in before:
            for vip in before[vip_type]:
                new_ips.remove(vip)
        if len(new_ips) > 1:
            raise Exception("Too many new IPs found, can't isolate fixed IP.")
        return new_ips[0]

    def check_ip(self, ip, port):
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
            info = {"address": self.msg['ip']}
            nova.action(node_id, "removeFixedIp", info, admin=True)
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
        #LOG.info("Fixed IP mode does not require IP deletion")
        LOG.info("Fixed IP placeholder {0} deleted".format(self.msg['ip']))
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg
