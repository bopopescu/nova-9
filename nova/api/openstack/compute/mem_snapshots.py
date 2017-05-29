# Copyright 2011 OpenStack Foundation
# Copyright 2013 IBM Corp.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.


import time

from nova.api.openstack import common
from nova.api.openstack.compute.schemas import mem_snapshots
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api import validation
from nova import compute
from nova.compute import power_state
from nova.compute import task_states
from nova.compute import vm_states
from nova import exception
from nova.policies import mem_snapshots as ms_policies

from ics_sdk import manager
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

ALIAS = "memsnapshots"

class MemSnapshotsController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(MemSnapshotsController, self).__init__(*args, **kwargs)
        user = 'admin'
        passwd = 'admin@inspur'
        self.ics_manager = manager.Manager(user, passwd, 'https://100.2.30.85')
        self.compute_api = compute.API()

    def test(self, req, id):
        return {'id' : id}

    @extensions.expected_errors((400, 403, 404, 409))
    @validation.schema(mem_snapshots.create_mem_snapshots)
    def create(self, req, id, body):
        """Create memory snapshots for a server instance.
        """

        context = req.environ["nova.context"]
        context.can(ms_policies.BASE_POLICY_NAME)

        instance = common.get_instance(self.compute_api, context, id)

        #check if instance is active
        if instance.vm_state != vm_states.ACTIVE:
            resp = {
                'err_status' : 'error',
                'err_msg' : 'The instance should be active.'
            }

            return resp

        #paramter process
        snapshot_name = common.normalize_name(body["snapshot_name"])
        description = body['description'] if body.get('description') else None
        memory = True

        #set instance task_state with IMAGE_BACKUP
        instance.task_state = task_states.MEMORY_SNAPSHOTS
        instance.save(expected_task_state=[None])

        try:
            # call ics sdk
            LOG.info('Start create memory snapshot')
            #ics_resp = self.ics_manager.create_mem_snapshots(id, snapshot_name, description, memory)
            time.sleep(30)
            #raise Exception('call ics sdk error')
        except Exception as e:
            resp = {
                'err_status' : 'error',
                'err_msg' : e.message
            }

            # reset instance state
            instance.task_state = None
            instance.save(expected_task_state=task_states.MEMORY_SNAPSHOTS)

            # return result
            return resp

        #reset instance state
        instance.task_state = None
        instance.save(expected_task_state=task_states.MEMORY_SNAPSHOTS)

        #return result
        resp = {
            'err_status' : 'ok',
            'result' : {
                'snapshot_id' : 'xxxxxx-yyyyyy-zzzzzz'
            }
        }

        return resp

    @extensions.expected_errors((400, 403, 404, 409))
    @validation.schema(mem_snapshots.restore_mem_snapshots)
    def restore(self, req, id, body):
        """Restore memory snapshots for a server instance.
        """

        context = req.environ["nova.context"]
        context.can(ms_policies.BASE_POLICY_NAME)

        instance = common.get_instance(self.compute_api, context, id)

        # check if instance is stopped
        if instance.vm_state != vm_states.STOPPED:
            resp = {
                'err_status': 'error',
                'err_msg': 'The instance should be stopped.'
            }

            return resp

        # set instance task_state with IMAGE_BACKUP
        instance.task_state = task_states.RESTORE_MEMORY_SNAPSHOTS
        instance.save(expected_task_state=[None])

        try:
            # call ics sdk
            LOG.info('Start restore memory snapshot')
            #ics_resp = self.ics_manager.restore_mem_snapshots(id, snapshot_id)
            time.sleep(30)
            #raise Exception('call ics sdk error')
        except Exception as e:
            resp = {
                'err_status' : 'error',
                'err_msg' : e.message
            }

            # reset instance state
            instance.task_state = None
            instance.save(expected_task_state=task_states.RESTORE_MEMORY_SNAPSHOTS)

            # return result
            return resp

        # reset instance state
        instance.task_state = None
        instance.save(expected_task_state=task_states.RESTORE_MEMORY_SNAPSHOTS)

        #set instance vm_state with active
        instance.vm_state = vm_states.ACTIVE
        instance.save(expected_vm_state=vm_states.STOPPED)

        #set instance power_state with
        instance.power_state = power_state.RUNNING
        instance.save()

        # return result
        resp = {
            'err_status': 'ok',
            'result': {}
        }

        return resp


class MemSnapshots(extensions.V21APIExtensionBase):
    """Memory snapshots support."""

    name = "MemSnapshots"
    alias = ALIAS
    version = 1

    def get_controller_extensions(self):
        return []

    def get_resources(self):
        m_actions = {'create' : 'POST', 'restore' : 'POST', 'test': 'GET'}
        resource = [extensions.ResourceExtension(ALIAS, MemSnapshotsController(), member_actions=m_actions)]

        return resource
