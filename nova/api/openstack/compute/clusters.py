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

"""The clusters admin extension."""

from oslo_log import log as logging

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova.policies import clusters as cl_policies
from ics_sdk import session as ics_session

LOG = logging.getLogger(__name__)

ALIAS = "clusters"


class ClustersController(wsgi.Controller):
    """The Clusters API controller for the OpenStack API."""

    def __init__(self):
        self.ics_manager = ics_session.get_session()
        super(ClustersController, self).__init__()

    @extensions.expected_errors(404)
    def hosts(self, req, id):
        context = req.environ['nova.context']
        context.can(cl_policies.BASE_POLICY_NAME)
        id = id.replace('ics.', '')
        ics_hosts = self.ics_manager.host.get_hosts_in_cluster(id)
        hosts = []
        keys = ['id',
                'clusterId',
                'clusterName',
                'name',  # ip
                'logicalProcessor',
                'cpuUsage',
                'totalMem',
                'memoryUsage',
                'pnicNum',
                'status']
        for ics_host in ics_hosts:
            host = {}
            for k in keys:
                host[k] = ics_host.get(k)
            host['ip'] = ics_host.get('name')
            host['totalMem'] = int(round(ics_host.get('totalMem')))
            hosts.append(host)
        return dict(hosts=hosts)


class Clusters(extensions.V21APIExtensionBase):
    """Admin-only cluster administration."""

    name = "Clusters"
    alias = ALIAS
    version = 1

    def get_resources(self):
        m_actions = {'hosts': 'GET'}
        resources = [extensions.ResourceExtension(ALIAS, ClustersController(),
                                                  member_actions=m_actions)]

        return resources

    def get_controller_extensions(self):
        return []
