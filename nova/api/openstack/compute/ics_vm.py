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

# from ics_sdk import session

import time
import json
from nova.policies import ics_vm as ics_vm_pl
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
        #  self._ics_manager = session.get_session()
        self._ics_manager = None
        #  self._get_ics_session()
        self._compute_api = compute.API()
        self._image_api = nova.image.API()
        super(IcsVmController, self).__init__()

    # Define support for GET on a collection
    def index(self, req):
        data = {'param': 'test'}
        return data
  
    def _get_ics_session(self):
        if self._ics_manager:
            return True
        try:
            from ics_sdk import session
            self._ics_manager = session.get_session()
            return True
        except:
            self._ics_manager = None
            return False
    

    @extensions.expected_errors((404, 412, 500))
    @validation.schema(ics_vm.mount)
    def mount(self, req, body):
        """mount iso to vm """
        context = req.environ['nova.context']
        context.can(ics_vm_pl.BASE_POLICY_NAME)
        vmid = body['vmid']
        isoid = body['isoid']
        if not self._get_ics_session():
            raise webob.exc.HTTPServerError(explanation="ics connect failed !")

        image = self._validate_image(context, isoid)
        if image.get('disk_format')!= 'iso' and image.get('disk_format')!= 'ISO' :
            explanation = _("diskformat must be iso.")
            raise webob.exc.HTTPPreconditionFailed(explanation=explanation)
        self._validate_vm(context, vmid)
        # do ics-vm mount iso
        LOG.info("begin to mount iso to ics_vm : %s", vmid)
        try:
            task_info = self._ics_manager.vm.attach_cdrom(vm_id=vmid, isoid=isoid)
        except Exception as e:
            # do something
            LOG.error("mount iso to ics_vm exception : " + e.message)
            raise webob.exc.HTTPServerError(explanation=e.message)
        LOG.info("end to mount iso to ics_vm : %s", vmid)
        state = task_info['state']
        if state == 'FINISHED':
            res = {'success': True}
        else:
            res = {'success': False}

        return dict(vmMount=res)

    @extensions.expected_errors((404, 500))
    @validation.schema(ics_vm.unmount)
    def unmount(self, req, body):
        """unmount iso to vm """
        context = req.environ['nova.context']
        context.can(ics_vm_pl.BASE_POLICY_NAME)
        if not self._get_ics_session():
            raise webob.exc.HTTPServerError(explanation="ics connect failed !")
        
        vmid = body['vmid']
        self._validate_vm(context, vmid)
        # do ics-vm unmount iso
        LOG.info("begin to unmount iso to ics_vm")
        try:
            task_info = self._ics_manager.vm.detach_cdrom(vm_id=vmid)
        except Exception as e:
            # do something
            LOG.error("unmount iso to ics_vm exception : " + e.message)
            raise webob.exc.HTTPServerError(explanation=e.message)
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

    @extensions.expected_errors((404, 500))
    def get_boot_volume_id(self, req, id):
        try:
            context = req.environ['nova.context']
            context.can(ics_vm_pl.BASE_POLICY_NAME)
            if not self._get_ics_session():
                return dict(boot_volume_id='', error='CANNOT_CONNECT_ICS')
            boot_volume_id = ''
            vm_info = self._ics_manager.vm.get_info(id)
            for disk in vm_info['disks']:
                if disk['volume']['bootable']:
                    boot_volume_id = disk['volume']['id']
            return dict(boot_volume_id=boot_volume_id, error='')
        except Exception as e:
            return dict(boot_volume_id='', error=e.message)


    @extensions.expected_errors(500)
    def icsHostProcessor(self, req, id):
        """query logicalProcessor of ics_host """
        context = req.environ['nova.context']
        context.can(ics_vm_pl.BASE_POLICY_NAME)
        if not self._get_ics_session():
            raise webob.exc.HTTPServerError(explanation="ics connect failed !")
        try:
            hostInfo = self._ics_manager.host.get_host(id)
        except Exception as e:
            # do something
            LOG.error("query logicalProcessor of ics_host  exception : " + e.message)
            raise webob.exc.HTTPServerError(explanation=e.message)
        if 'logicalProcessor' in hostInfo :
            return dict(logicalProcessor=hostInfo['logicalProcessor'])
	elif 'message' in hostInfo :
            raise webob.exc.HTTPServerError(explanation=hostInfo['message'])
        else :
            raise webob.exc.HTTPServerError(explanation="there is no logicalProcessor in ics_host: "+id)
     
    @extensions.expected_errors(500)
    def icsGuestOs(self, req):
        """query ics_vm os all of it """
        context = req.environ['nova.context']
        context.can(ics_vm_pl.BASE_POLICY_NAME)
        if not self._get_ics_session():
           raise webob.exc.HTTPServerError(explanation="ics connect failed !")
        try:
           res = self._ics_manager.vm.get_guestos()
        except Exception as e:
           # do something
           LOG.error("query logicalProcessor of ics_host  exception : " + e.message)
           raise webob.exc.HTTPServerError(explanation=e.message)
        return dict(guestsOs=res)

    @validation.schema(ics_vm.attach_usb)
    def attach_usb(self, req, id, body):
        context = req.environ['nova.context']
        context.can(ics_vm_pl.BASE_POLICY_NAME)
        vm_id = id
        LOG.debug('Receive ICM request to attach USB to VM "%s", '
                  'parameter is "%s".' % (vm_id, json.dumps(body)))
        # connect ICS
        if not self._get_ics_session():
            return dict(result='fail', error='CANNOT_CONNECT_ICS')
        # begin to attach
        bus = body.get('bus')
        device = body.get('device')
        releaseAfterPowerOff = body.get('releaseAfterPowerOff')
        try:
            task = self._ics_manager.vm.attach_usb(vm_id,
                                                   bus,
                                                   device,
                                                   releaseAfterPowerOff)
        except Exception as e:
            LOG.error('Error to attach USB to VM "%s", USB data is "%s", '
                      'error message is "%s".'
                      % (vm_id, json.dumps(body), e.message))
            return dict(result='fail', error=e.message)
        # check result
        if self._attach_usb_result(vm_id, bus, device):
            return dict(result='success',
                        error='')
        else:
            return dict(result='fail',
                        error='Error to attach USB to VM %s' % vm_id)

    def detach_usb(self, req, id, body):
        context = req.environ['nova.context']
        context.can(ics_vm_pl.BASE_POLICY_NAME)
        vm_id = id
        LOG.debug('Receive ICM request to detach USB from VM "%s".' % vm_id)
        # connect ICS
        if not self._get_ics_session():
            return dict(result='fail', error='CANNOT_CONNECT_ICS')
        # begin to detach
        try:
            task = self._ics_manager.vm.detach_usb(vm_id)
        except Exception as e:
            LOG.error('Error to detach USB from VM "%s", '
                      'error message is "%s".'
                      % (vm_id, e.message))
            return dict(result='fail', error=e.message)
        # check result
        if self._detach_usb_result(vm_id):
            return dict(result='success',
                        error='')
        else:
            return dict(result='fail',
                        error='Error to detach USB from VM %s' % vm_id)

    def _attach_usb_result(self, vm_id, bus, device):
        retry = 0
        while retry <= 10:
            retry = retry + 1
            time.sleep(1)
            usb_info = self._get_usb_info(vm_id)
            if usb_info == 'ERROR':
                continue
            if usb_info.get('bus') == bus and \
                    usb_info.get('device') == device:
                return True
        return False

    def _detach_usb_result(self, vm_id):
        retry = 0
        while retry <= 10:
            retry = retry + 1
            time.sleep(1)
            usb_info = self._get_usb_info(vm_id)
            if usb_info == 'ERROR':
                continue
            if not usb_info:
                return True
        return False

    def _get_usb_info(self, vm_id):
        try:
            vm_info = self._ics_manager.vm.get_info(vm_id)
            return vm_info.get('usb')
        except Exception as e:
            LOG.error('Error to get VM USB info from ICS, VM ID is "%s", '
                      'error message is "%s".' % (vm_id, e.message))
            return 'ERROR'


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
            'icsGuestOs': 'GET'
        }
        m_actions = {'get_boot_volume_id': 'GET',
                     'icsHostProcessor': 'GET',
                     'attach_usb': 'POST',
                     'detach_usb': 'POST'}

        res = extensions.ResourceExtension(ALIAS, IcsVmController(),
                                           collection_actions=coll_actions,
                                           member_actions=m_actions)
        return [res]

    def get_controller_extensions(self):
        return []
