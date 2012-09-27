#!/usr/bin/env python
# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

from novaclient import client


class Node(object):
    def __init__(self, username, password, tenant, auth_url, region):
        self.nova = client.HTTPClient(
            username, password, tenant, auth_url, region, 'compute'
        )

    def create(self, node_id, image, node_type):
        url = "/servers"
        body = {"server": {
                "name": 'lbass_{0}'.format(node_id),
                "imageId": image,
                "flavourId": node_type,
                }}
        resp, body = self.nova.post(url, body)
        return body

    def status(self, node_id):
        """ used to keep scanning to see if node is up """