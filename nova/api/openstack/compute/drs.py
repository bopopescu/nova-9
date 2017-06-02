# Copyright 2012 IBM Corp.
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

from oslo_log import log as logging
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack.compute.views import hypervisors as hyper_view
from ics_sdk import session as ics_session

LOG = logging.getLogger(__name__)

ALIAS = 'drs'


class DRSController(wsgi.Controller):

    _view_builder_class = hyper_view.ViewBuilder

    def __init__(self):
        self.ics_manager = ics_session.get_session()
        super(DRSController, self).__init__()

    @extensions.expected_errors((400, 404))
    def setdrs(self, req, id, body):

        id = id.replace('ics.', '')
        rs = self.ics_manager.cluster.set_cluster_drs(id, body['value'])

        re = "False"
        if rs["state"] == "FINISHED":
            re = "True"

        return re

    @extensions.expected_errors((400, 404))
    def setdpm(self, req, id, body):

        id = id.replace('ics.', '')
        self.ics_manager.cluster.set_cluster_drs(id, body['value'])
        rs = self.ics_manager.cluster.set_cluster_dpm(id, body['value'])

        re = "False"
        if rs["state"] == "FINISHED":
            re = "True"

        return re

    @extensions.expected_errors((400, 404))
    def checkdrs(self, req, id):

        id = id.replace('ics.', '')
        rs = self.ics_manager.cluster.check_cluster_drsstate(id)

        return str(rs)

    @extensions.expected_errors((400, 404))
    def checkdpm(self, req, id):

        id = id.replace('ics.', '')
        rs = self.ics_manager.cluster.check_cluster_dpmstate(id)

        return str(rs)


class DRSClass(extensions.V21APIExtensionBase):
    """Fixed IPs support."""

    name = "DRS"
    alias = ALIAS
    version = 1

    def get_resources(self):
        member_actions = {'setdrs': 'POST', 'setdpm': 'POST', 'checkdrs': 'GET', 'checkdpm': 'GET'}
        resources = extensions.ResourceExtension(ALIAS,
                                                DRSController(),
                                                member_actions=member_actions)
        return [resources]

    def get_controller_extensions(self):
        return []
