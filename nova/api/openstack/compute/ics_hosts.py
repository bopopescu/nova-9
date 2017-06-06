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

"""The ics nodes admin extension."""

from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi

from ics_sdk import session
from ics_sdk.utils import log
import json

LOG = logging.getLogger(__name__)

ALIAS = "icsHosts"


class IcsHostsController(wsgi.Controller):
    """The ICS Nodes API controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(IcsHostsController, self).__init__()
    
    def _get_ics_session(self):
        if self.ics_manager:
            return True
        try:
            self.ics_manager = session.get_session()
            return True
        except:
            self.ics_manager = None
            return False 

    @extensions.expected_errors(404)
    def vms(self, req, id):

        if not self._get_ics_session():
            return dict(vms=[], error='CANNOT_CONNECT_ICS')

        if not id:
            return dict(vms=[], error='HOST_ID_NULL')

        ics_host = self.ics_manager.host.get_host(id)
        tmp = ics_host.get('message')
        if tmp:
            return dict(vms=[], error='HOST_NOT_EXIST')

        ics_vms = self.ics_manager.vm.get_vms_in_host(id)
        vms = []
        keys = ['id', 'name', 'status', 'cpuNum', 'memory', 'disks',
                'nics', 'hostId', 'hostName']
        for ics_vm in ics_vms:
            vm = {}
            for k in keys:
                vm[k] = ics_vm.get(k)
            vms.append(vm)
        return dict(vms=vms)


class IcsHosts(extensions.V21APIExtensionBase):
    """Admin-only node administration."""

    name = "IcsHosts"
    alias = ALIAS
    version = 1

    def get_resources(self):
        m_actions = {'vms': 'GET'}
        resources = [extensions.ResourceExtension(ALIAS, IcsHostsController(),
                                                  member_actions=m_actions)]

        return resources

    def get_controller_extensions(self):
        return []
