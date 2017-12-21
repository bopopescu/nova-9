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

"""The wsthost admin extension."""

import json
import traceback
from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import wsthost as wsthost_policies

LOG = logging.getLogger(__name__)

ALIAS = "wsthost"


class WsthostController(wsgi.Controller):
    """The Wsthost API controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(WsthostController, self).__init__()

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
        data = {'param': 'test wsthost'}
        return data

    @extensions.expected_errors(404)
    def wsthostmessage(self, req, id):
        context = req.environ['nova.context']
        context.can(wsthost_policies.BASE_POLICY_NAME)
        host_id = id
        try:
            if not self._get_ics_session():
                return dict(hosts=[], error='CANNOT_CONNECT_ICS')
            host_info = self.ics_manager.host.get_host(host_id)
            LOG.info('--Get host info from ICS-- : ' + json.dumps(host_info))
            return dict({'host_id':host_id, 'host_info':host_info})
        except Exception as e:
            LOG.error('Error to get host info from ICS : ' + traceback.format_exc())
            return dict(host_info=[], error=e.message)
        

class Wsthost(extensions.V21APIExtensionBase):
    """Admin-only cluster administration."""

    name = "Wsthost"
    alias = ALIAS
    version = 1

    def get_resources(self):
        m_actions = {'wsthostmessage': 'GET'}
        resources = [extensions.ResourceExtension(ALIAS, WsthostController(),
                                                  member_actions=m_actions)]
        return resources

    def get_controller_extensions(self):
        return []

