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


class NotFound(Exception):
    pass


class BuildIpDriver(IpDriver.BuildIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info("Creating a requested floating IP")
        try:
            url = '/os-floating-ips'
            body = {"pool": None}
            resp, body = nova.nova.post(url, body=body)
            ip_info = body['floating_ip']
        except exceptions.ClientException:
            LOG.exception(
                'Error getting a Floating IP'
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg
        LOG.info("Floating IP {0} created".format(ip_info['id']))
        self.msg['id'] = ip_info['id']
        self.msg['ip'] = ip_info['ip']
        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class AssignIpDriver(IpDriver.AssignIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Assigning Floating IP {0} to {1}"
            .format(self.msg['ip'], self.msg['name'])
        )
        try:
            node_id = nova.get_node(self.msg['name'])
            LOG.info(
                'Node name {0} identified as ID {1}'
                .format(self.msg['name'], node_id)
            )
            info = {"address": self.msg['ip']}
            nova.action(node_id, "addFloatingIp", info)
            if cfg.CONF['mgm']['tcp_check_port']:
                self.check_ip(self.msg['ip'],
                              cfg.CONF['mgm']['tcp_check_port'])
        except:
            LOG.exception(
                'Error assigning Floating IP {0} to {1}'
                .format(self.msg['ip'], self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

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
        self.rm_fip_ignore_500 = cfg.CONF['mgm']['rm_fip_ignore_500']

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Removing Floating IP {0} from {1}"
            .format(self.msg['ip'], self.msg['name'])
        )
        try:
            node_id = nova.get_node(self.msg['name'])
            info = {"address": self.msg['ip']}
            try:
                nova.action(node_id, "removeFloatingIp", info)
            except exceptions.ClientException as e:
                if not (e.code == 500 and self.rm_fip_ignore_500):
                    raise
        except:
            LOG.exception(
                'Error removing Floating IP {0} from {1}'
                .format(self.msg['ip'], self.msg['name'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg


class DeleteIpDriver(IpDriver.DeleteIpDriver):

    def __init__(self, msg):
        self.msg = msg

    def _find_vip_id(self, nova, vip):
        url = '/os-floating-ips'
        resp, body = nova.nova.get(url)
        for fip in body['floating_ips']:
            if fip['ip'] == vip:
                return fip['id']
        raise NotFound('floating IP not found')

    def run(self):
        try:
            nova = Node()
        except Exception:
            LOG.exception("Error initialising Nova connection")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        LOG.info(
            "Deleting Floating IP {0}"
            .format(self.msg['ip'])
        )
        try:
            vip = self.msg['ip']
            vip_id = self._find_vip_id(nova, vip)
            url = '/os-floating-ips/{0}'.format(vip_id)
            # sometimes this needs to be tried twice
            try:
                resp, body = nova.nova.delete(url)
            except exceptions.ClientException:
                resp, body = nova.nova.delete(url)
        except:
            LOG.exception(
                'Error deleting Floating IP {0}'
                .format(self.msg['ip'])
            )
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg

        self.msg[self.RESPONSE_FIELD] = self.RESPONSE_SUCCESS
        return self.msg
