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

"""The wstvms admin extension."""

import json
import traceback
from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import wstvms as wstvms_policies

LOG = logging.getLogger(__name__)

ALIAS = "wstvms"


class WstvmsController(wsgi.Controller):
    """The Wstvms API controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(WstvmsController, self).__init__()

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

    # Define support for GET on a collection
    def index(self, req):
        data = {'param': 'test wstvms'}
        return data

    @extensions.expected_errors(404)
    def wstvmsmessage(self, req, id):
        #ics_vms = self.ics_manager.vm.get_vms_in_host(id)
        context = req.environ['nova.context']
        context.can(wstvms_policies.BASE_POLICY_NAME)
        vm_id = id
        try:
            if not self._get_ics_session():
                return dict(hosts=[], error='CANNOT_CONNECT_ICS')
            vm_info = self.ics_manager.vm.get_info(vm_id)
            LOG.info('--Get vm info from ICS-- : ' + json.dumps(vm_info))
            return dict({'vmid':vm_id, 'vm_info':vm_info})
        except Exception as e:
            LOG.error('Error to get vm info from ICS : ' + traceback.format_exc())
            return dict(vcpu_qos=[], error=e.message)
        

class Wstvms(extensions.V21APIExtensionBase):
    """Admin-only cluster administration."""

    name = "Wstvms"
    alias = ALIAS
    version = 1

    def get_resources(self):
        m_actions = {'wstvmsmessage': 'GET'}
        resources = [extensions.ResourceExtension(ALIAS, WstvmsController(),
                                                  member_actions=m_actions)]
        return resources

    def get_controller_extensions(self):
        return []

