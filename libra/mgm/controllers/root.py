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

from libra.mgm.controllers.build import BuildController
from libra.mgm.controllers.delete import DeleteController
from libra.mgm.controllers.vip.drivers.base import known_drivers
from libra.openstack.common import log
from libra.openstack.common import importutils

from oslo.config import cfg


LOG = log.getLogger(__name__)


class PoolMgmController(object):

    ACTION_FIELD = 'action'
    RESPONSE_FIELD = 'response'
    RESPONSE_SUCCESS = 'PASS'
    RESPONSE_FAILURE = 'FAIL'

    def __init__(self, json_msg):
        self.msg = json_msg

    def run(self):
        if self.ACTION_FIELD not in self.msg:
            LOG.error("Missing `{0}` value".format(self.ACTION_FIELD))
            self.msg[self.RESPONSE_FILED] = self.RESPONSE_FAILURE
            return self.msg

        action = self.msg[self.ACTION_FIELD].upper()

        self.ip_driver = known_drivers[cfg.CONF['mgm']['ip_driver']]

        try:
            if action == 'BUILD_DEVICE':
                controller = BuildController(self.msg)
            elif action == 'DELETE_DEVICE':
                controller = DeleteController(self.msg)
            elif action == 'BUILD_IP':
                BuildIpDriver = importutils.import_class('.'.join((self.ip_driver, "BuildIpDriver")))
                controller = BuildIpDriver(self.msg)
            elif action == 'ASSIGN_IP':
                AssignIpDriver = importutils.import_class('.'.join((self.ip_driver, "AssignIpDriver")))
                controller = AssignIpDriver(self.msg)
            elif action == 'REMOVE_IP':
                RemoveIpDriver = importutils.import_class('.'.join((self.ip_driver, "RemoveIpDriver")))
                controller = RemoveIpDriver(self.msg)
            elif action == 'DELETE_IP':
                DeleteIpDriver = importutils.import_class('.'.join((self.ip_driver, "DeleteIpDriver")))
                controller = DeleteIpDriver(self.msg)
            else:
                LOG.error(
                    "Invalid `{0}` value: {1}".format(
                        self.ACTION_FIELD, action
                    )
                )
                self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
                return self.msg
            self.msg = controller.run()
            # Delete a built device if it has failed
            if (
                action == 'BUILD_DEVICE'
                and self.msg[self.RESPONSE_FIELD] == self.RESPONSE_FAILURE
                and 'name' in self.msg
            ):
                delete_msg = {'name': self.msg['name']}
                controller = DeleteController(delete_msg)
                controller.run()

            return self.msg
        except Exception:
            LOG.exception("Controller exception")
            self.msg[self.RESPONSE_FIELD] = self.RESPONSE_FAILURE
            return self.msg
