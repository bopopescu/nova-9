# Copyright (c) 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""The hostnic admin extension."""

from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import hostnic as al_policies

LOG = logging.getLogger(__name__)

ALIAS = "hostnic"


class HostnicController(wsgi.Controller):
    """The Hostnic API controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(HostnicController, self).__init__()

    def _get_ics_session(self):
        if self.ics_manager:
            return True
        try:
            from ics_sdk import session
            self.ics_manager = session.get_session()
            return True
        except:
            self.ics_manager = None
            return False

    @extensions.expected_errors(404)
    def freenic(self, req, id):
        try:
            nic = self.ics_manager.host.get_freenic_in_host(id)
            renic = "["
            if nic:
                for i in range(len(nic)):
                    renic += "{"
                    for key,value in nic[i].items():
                        renic += "\"" + str(key) +  "\":\"" + str(value) + "\","
                    renic = renic[:-1]
                    renic += "},"
                renic = renic[:-1]
            renic += "]"
            return  renic
        except Exception,e:
            print e
 

class Hostnic(extensions.V21APIExtensionBase):
    """Admin-only cluster administration."""

    name = "Hostnic"
    alias = ALIAS
    version = 1

    def get_resources(self):
        m_actions = {'freenic': 'GET'}
        resources = [extensions.ResourceExtension(ALIAS, HostnicController(),
                                                  member_actions=m_actions)]
        return resources

    def get_controller_extensions(self):
        return []

