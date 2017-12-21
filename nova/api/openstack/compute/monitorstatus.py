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

"""The monitorstatus admin extension."""

from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import monitorstatus as al_policies
from nova.volume import cinder
from nova.image import glance
from nova.compute import api
from nova.network import api as networkapi
from nova.db import api as dbapi
from nova.api.openstack import api_version_request

LOG = logging.getLogger(__name__)
ALIAS = "monitorstatus"


class MonitorstatusController(wsgi.Controller):
    """The Monitorstatus API controller for the OpenStack API."""

    def __init__(self):
        self.cinder_api = cinder.API()
        self.network_api = networkapi.API()
        self.aggregate_api = api.AggregateAPI()
        #self.api_version_request = api_version_request.APIVersionRequest()
        super(MonitorstatusController, self).__init__()

    @extensions.expected_errors(404)
    def monitorstatusmessage(self, req ):

        context = req.environ['nova.context']
        statusdict = {'nova': '0', 'glance': '0', 'cinder': '0' , 'neutron': '0' , 'keystone': '0' , 'mysql': '0' ,'rabbitmq': '0'}
        
        for (key,value) in statusdict.items():
          try:
            if key == 'cinder':
              self.cinder_api.get_all(context)
            elif key == 'glance':
              glance.get_default_image_service()
            elif key == 'nova':
              self.aggregate_api.get_aggregate_list(context)
            elif key == 'neutron':
              self.network_api.get_all(context)
            elif key == 'db':
              dbapi.service_get_all(context)
            elif key == 'rabbitmq' or key == 'keystone':
              api_version_request.min_api_version()
          except Exception,e:
            statusdict[key] = '1'
            #print str(e)
          #print "key:"+key+";;;;;value:"+statusdict[key]
 
        return  statusdict
        

class Monitorstatus(extensions.V21APIExtensionBase):
    """Admin-only cluster administration."""

    name = "Monitorstatus"
    alias = ALIAS
    version = 1

    def get_resources(self):
        c_actions = {'monitorstatusmessage': 'GET'}
        resources = [extensions.ResourceExtension(ALIAS, MonitorstatusController(),
                                                  collection_actions=c_actions)]
        return resources


    def get_controller_extensions(self):
        return []
