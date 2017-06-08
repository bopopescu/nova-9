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

from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import wsthost as al_policies
from ics_sdk import session as ics_session

LOG = logging.getLogger(__name__)

ALIAS = "wsthost"


class WsthostController(wsgi.Controller):
    """The Wsthost API controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = ics_session.get_session()
        super(WsthostController, self).__init__()

    @extensions.expected_errors(404)
    def wsthostmessage(self, req, id):
        print id
        return  self.ics_manager.host.get_host(id)
        

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

