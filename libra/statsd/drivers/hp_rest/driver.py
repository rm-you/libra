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

from libra.statsd.drivers.base import AlertDriver
from libra.statsd.admin_api import AdminAPI


class HPRestDriver(AlertDriver):
    def send_alert(self, message, device_id):
        api = AdminAPI(self.args.api_server, self.logger)
        if api.is_online():
            api.fail_device(device_id)
