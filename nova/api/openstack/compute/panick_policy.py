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

"""The collapse policy admin extension."""

from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import panick_policy as panick_policies

LOG = logging.getLogger(__name__)

ALIAS = "panick-policy"

class PanickPolicyController(wsgi.Controller):
    """The panick policy API controller for OpenStack API"""
    
    def __init__(self):
        from ics_sdk import session

        self.ics_manager = session.get_session()
        super(PanickPolicyController, self).__init__()

    @extensions.expected_errors(404)
    def setPanickPolicy(self, req, id, body):
        context = req.environ['nova.context']
        context.can(panick_policies.BASE_POLICY_NAME)
        #call ics_sdk
        res = {'flag':True, 'errorMessage':None, 'resData':None}
        try:
            vm_obj = self.ics_manager.vm.get_info(id)
            vm_obj['panickPolicy'] = body['panickPolicy']
            taskId = self.ics_manager.vm.edit_vm(id, vm_obj)
        except Exception as e:
            # do something
            LOG.error("set vm panick policy exception : " + e.message)
            res['flag'] = False
            res['errorMessage'] = e.message
            pass

        return dict(result=res)

    @extensions.expected_errors(404)
    def getPanickPolicy(self, req, id):
        # call ics_sdk
        res = {'flag': True, 'errorMessage': None, 'resData': None}
        try:
            vm_obj = self.ics_manager.vm.get_info(id)
            res['resData']={'vm_id' : id, 'panickPolicy' : vm_obj['panickPolicy']}
        except Exception as e:
            # do something
            LOG.error("get vm panick policy exception : " + e.message)
            res["flag"] = False
            res["errorMessage"] = e.message
            pass
        return dict(result=res)


class PanickPolicy(extensions.V21APIExtensionBase):
    """Panick Policy support"""

    name = "PanickPolicy"
    alias = ALIAS
    version = 1

    def get_resources(self):
        member_actions = {'setPanickPolicy': 'POST', 'getPanickPolicy': 'GET'}
        resource = extensions.ResourceExtension(
            ALIAS, PanickPolicyController(),
            member_actions=member_actions)
        return [resource]

    def get_controller_extensions(self):
        return []
