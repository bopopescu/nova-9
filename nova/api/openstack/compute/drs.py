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
from nova.policies import drs as cl_policies
from nova.api import validation
from nova.api.openstack.compute.schemas import drs

LOG = logging.getLogger(__name__)

ALIAS = 'drs'


class DRSController(wsgi.Controller):

    _view_builder_class = hyper_view.ViewBuilder

    def __init__(self):
        try:
            self.ics_manager = ics_session.get_session()
            super(DRSController, self).__init__()
        except Exception, e:
            return "Error: ICS get_session! %s" %e

    @extensions.expected_errors((400, 404))
    @validation.schema(drs.setdrs)
    def setdrs(self, req, id, body):

        context = req.environ['nova.context']
        context.can(cl_policies.BASE_POLICY_NAME)
        id = id.replace('ics.', '')
        try:
            rs = self.ics_manager.cluster.set_cluster_drs(id, body['value'])
        except Exception, e:
            return "Error: ICS set_cluster_drs! %s" %e

        re = "False"
        if rs["state"] == "FINISHED":
            re = "True"

        return {'setdrs%s'  %(body['value'] == 'True' and 'On' or 'Off'): re}

    @extensions.expected_errors((400, 404))
    @validation.schema(drs.setdrs)
    def setdpm(self, req, id, body):

        context = req.environ['nova.context']
        context.can(cl_policies.BASE_POLICY_NAME)
        id = id.replace('ics.', '')
        try:
            self.ics_manager.cluster.set_cluster_drs(id, body['value'])
            rs = self.ics_manager.cluster.set_cluster_dpm(id, body['value'])
        except Exception, e:
            return "Error: ICS set_cluster_dpm! %s" %e

        re = "False"
        if rs["state"] == "FINISHED":
            re = "True"

        return {'setdpm%s' %(body['value'] == 'True' and 'On' or 'Off'): re}

    @extensions.expected_errors((400, 404))
    def checkdrs(self, req, id):

        context = req.environ['nova.context']
        context.can(cl_policies.BASE_POLICY_NAME)
        id = id.replace('ics.', '')
        try:
            rs = self.ics_manager.cluster.check_cluster_drsstate(id)
        except Exception, e:
            return "Error: ICS check_cluster_drsstate! %s" %e

        return {'checkdrs': rs and 'On' or 'Off'}

    @extensions.expected_errors((400, 404))
    def checkdpm(self, req, id):

        context = req.environ['nova.context']
        context.can(cl_policies.BASE_POLICY_NAME)
        id = id.replace('ics.', '')
        try:
            rs = self.ics_manager.cluster.check_cluster_dpmstate(id)
        except Exception, e:
            return "Error: ICS check_cluster_dpmstate! %s" %e

        return {'checkdpm': rs and 'On' or 'Off'}


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
