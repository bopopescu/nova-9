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

import json
import traceback
import webob.exc
from oslo_log import log as logging

from nova.api.openstack import api_version_request
from nova.api.openstack.compute.schemas import cpu_priority
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api import validation
from nova import compute
from nova import exception
from nova.i18n import _
from nova.policies import cpu_priority as cp_policies
from nova import servicegroup
from nova import utils


ALIAS = "cpupriority"

LOG = logging.getLogger(__name__)


class CpuPriorityController(wsgi.Controller):
    """The ics node cpu priority controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = None
        self._get_ics_session()
        super(CpuPriorityController, self).__init__()

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

    #Define support for GET on a collection
    def index(self, req):
        data = {'param': 'test cpupriority'}
        return data

    @extensions.expected_errors(404)
    def show(self, req, id):
        """Return detailed information cpu priority about a specific server.
        :param req: `wsgi.Request` object
        :param id: Server identifier
        """
        context = req.environ['nova.context']
        context.can(cp_policies.BASE_POLICY_NAME)
        vm_id = id
        try:
            if not self._get_ics_session():
                return dict(hosts=[], error='CANNOT_CONNECT_ICS')
            vcpushares = self.ics_manager.vm.get_vcpu_shares(vm_id)
            LOG.info('--Get cpu priority of vm from ICS-- : ' + json.dumps(vcpushares))
            return dict({'vmid':vm_id, 'vcpushares':vcpushares})
        except Exception as e:
            LOG.error('Error to get cpu priority from ICS : ' + traceback.format_exc())
            return dict(vcpushares=[], error=e.message)

    @extensions.expected_errors((400, 403, 404, 409))
    @validation.schema(cpu_priority.cpupriority)
    def create(self, req, body):
        context = req.environ['nova.context']
        context.can(cp_policies.BASE_POLICY_NAME)
        vm_id = body.get('vmid')
        LOG.debug('Receive ICM request to set cpu priority of vm "%s", '
                  'parameter is "%s".' % (vm_id, json.dumps(body)))
        # connect ICS
        if not self._get_ics_session():
            return dict(result='fail', error='CANNOT_CONNECT_ICS')
        # begin to set or update
        vcpushares = 1024
        vcpushares = int(body.get('vcpushares'))
        try:
            task = self.ics_manager.vm.set_vcpu_shares(vm_id,vcpushares)
            return dict({'result':'success'})
        except Exception as e:
            LOG.error('Error to set cpu priority of vm "%s",  data is "%s", '
                      'error message is "%s".'
                      % (vm_id, json.dumps(body), e.message))
            return dict(result='fail', error=e.message)


class CpuPriority(extensions.V21APIExtensionBase):
    """CpuPriority."""

    name = "CpuPriority"
    alias = ALIAS
    version = 1

    def get_resources(self):
        #member_actions = {'action': 'POST'}
        #collection_actions = {'detail': 'GET', 'createIcsVm': 'POST'}
        resources = [
            extensions.ResourceExtension(
                ALIAS,
                CpuPriorityController(),
                member_name='cpupriority'
                )]

        return resources

    def get_controller_extensions(self):
        return []
