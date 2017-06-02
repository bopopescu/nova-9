# Copyright 2011-2012 OpenStack Foundation
# All Rights Reserved.
# Copyright 2013 Red Hat, Inc.
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

"""The ics-vm impl."""

from ics_sdk import session

# from nova.policies import ics_vm as ics_vm_pl
import webob.exc
from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.api.openstack.compute.schemas import ics_vm
from nova.api import validation
from nova import exception
from nova import compute
import nova.image

from nova.i18n import _

from nova.api.openstack import common

# import nova.conf

from oslo_log import log as logging

# CONF = nova.conf.CONF

LOG = logging.getLogger(__name__)

ALIAS = "os-ics-vm"


# ALIAS needs to be unique and should be of the format
# ^[a-z]+[a-z\-]*[a-z]$

class IcsVmController(wsgi.Controller):
    """icsvmController action : mount,unmount"""

    def __init__(self):
        """init work"""
        self._ics_manager = session.get_session()
        self._compute_api = compute.API()
        self._image_api = nova.image.API()
        super(IcsVmController, self).__init__()

    # Define support for GET on a collection
    def index(self, req):
        data = {'param': 'test'}
        return data

    @extensions.expected_errors(404)
    @validation.schema(ics_vm.mount)
    def mount(self, req, body):
        """mount iso to vm """
        context = req.environ['nova.context']
        vmid = body['vmid']
        isoid = body['isoid']
        self._validate_image(context, isoid)
        self._validate_vm(context, vmid)
        # do ics-vm mount iso
        LOG.info("begin to mount iso to ics_vm")
        try:
            task_info = self._ics_manager.vm.attach_cdrom(vm_id=vmid, isoid=isoid)
        except Exception as e:
            # do something
            LOG.error("mount iso to ics_vm exception : " + e.message)
            pass
        LOG.info("end to mount iso to ics_vm")
        state = task_info['state']
        if state == 'FINISHED':
            res = {'success': True}
        else:
            res = {'success': False}

        return dict(vmMount=res)

    @extensions.expected_errors(404)
    @validation.schema(ics_vm.unmount)
    def unmount(self, req, body):
        """unmount iso to vm """
        context = req.environ['nova.context']
        vmid = body['vmid']
        self._validate_vm(context, vmid)
        # do ics-vm unmount iso
        LOG.info("begin to unmount iso to ics_vm")
        try:
            task_info = self._ics_manager.vm.detach_cdrom(vm_id=vmid)
        except Exception as e:
            # do something
            LOG.error("unmount iso to ics_vm exception : " + e.message)
            pass
        LOG.info("end to unmount iso to ics_vm")
        state = task_info['state']
        if state == 'FINISHED':
            res = {'success': True}
        else:
            res = {'success': False}
        return dict(vmUnmount=res)

    def _validate_image(self, context, isoid):
        """check image is existed or not"""

        try:
            image = self._image_api.get(context, isoid)
        except (exception.ImageNotFound, exception.InvalidImageRef):
            explanation = _("Image not found.")
            raise webob.exc.HTTPNotFound(explanation=explanation)
        return image

    def _validate_vm(self, context, vmid):
        """check vm is existed or not"""
        instance = common.get_instance(self._compute_api, context,
                                       vmid, expected_attrs=None)
        return instance


class IcsVm(extensions.V21APIExtensionBase):
    """IcsVm object.
    """

    name = "icsvm"
    alias = ALIAS
    version = 1

    def get_resources(self):
        coll_actions = {
            'mount': 'POST',
            'unmount': 'POST',
        }

        res = extensions.ResourceExtension(ALIAS, IcsVmController(),
                                           collection_actions=coll_actions)
        return [res]

    def get_controller_extensions(self):
        return []
