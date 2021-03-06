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


import itertools

from nova.policies import admin_actions
from nova.policies import admin_password
from nova.policies import agents
from nova.policies import aggregates
from nova.policies import assisted_volume_snapshots
from nova.policies import attach_interfaces
from nova.policies import availability_zone
from nova.policies import baremetal_nodes
from nova.policies import base
from nova.policies import block_device_mapping
from nova.policies import block_device_mapping_v1
from nova.policies import cells
from nova.policies import cells_scheduler
from nova.policies import certificates
from nova.policies import cloudpipe
from nova.policies import config_drive
from nova.policies import console_auth_tokens
from nova.policies import console_output
from nova.policies import consoles
from nova.policies import create_backup
from nova.policies import deferred_delete
from nova.policies import evacuate
from nova.policies import extended_availability_zone
from nova.policies import extended_server_attributes
from nova.policies import extended_status
from nova.policies import extended_volumes
from nova.policies import extension_info
from nova.policies import extensions
from nova.policies import fixed_ips
from nova.policies import flavor_access
from nova.policies import flavor_extra_specs
from nova.policies import flavor_manage
from nova.policies import flavor_rxtx
from nova.policies import flavors
from nova.policies import floating_ip_dns
from nova.policies import floating_ip_pools
from nova.policies import floating_ips
from nova.policies import floating_ips_bulk
from nova.policies import fping
from nova.policies import hide_server_addresses
from nova.policies import hosts
from nova.policies import hypervisors
from nova.policies import image_metadata
from nova.policies import image_size
from nova.policies import images
from nova.policies import instance_actions
from nova.policies import instance_usage_audit_log
from nova.policies import ips
from nova.policies import keypairs
from nova.policies import limits
from nova.policies import lock_server
from nova.policies import migrate_server
from nova.policies import migrations
from nova.policies import multinic
from nova.policies import multiple_create
from nova.policies import networks
from nova.policies import networks_associate
from nova.policies import pause_server
from nova.policies import pci
from nova.policies import quota_class_sets
from nova.policies import quota_sets
from nova.policies import remote_consoles
from nova.policies import rescue
from nova.policies import scheduler_hints
from nova.policies import security_group_default_rules
from nova.policies import security_groups
from nova.policies import server_diagnostics
from nova.policies import server_external_events
from nova.policies import server_groups
from nova.policies import server_metadata
from nova.policies import server_password
from nova.policies import server_tags
from nova.policies import server_usage
from nova.policies import servers
from nova.policies import servers_migrations
from nova.policies import services
from nova.policies import shelve
from nova.policies import simple_tenant_usage
from nova.policies import suspend_server
from nova.policies import tenant_networks
from nova.policies import used_limits
from nova.policies import user_data
from nova.policies import versions
from nova.policies import virtual_interfaces
from nova.policies import volumes
from nova.policies import volumes_attachments
from nova.policies import wstvms
from nova.policies import wsthost
from nova.policies import cpu_priority
from nova.policies import mem_priority
from nova.policies import ics_hosts
from nova.policies import clusters 
from nova.policies import drs
from nova.policies import cpu_qos
from nova.policies import disk_qos
from nova.policies import hostnic
from nova.policies import ics_datastore
from nova.policies import panick_policy
from nova.policies import ics_vm
from nova.policies import monitorstatus
from nova.policies import mem_snapshots


def list_rules():
    return itertools.chain(
        admin_actions.list_rules(),
        admin_password.list_rules(),
        agents.list_rules(),
        aggregates.list_rules(),
        assisted_volume_snapshots.list_rules(),
        attach_interfaces.list_rules(),
        availability_zone.list_rules(),
        baremetal_nodes.list_rules(),
        base.list_rules(),
        block_device_mapping.list_rules(),
        block_device_mapping_v1.list_rules(),
        cells.list_rules(),
        cells_scheduler.list_rules(),
        certificates.list_rules(),
        cloudpipe.list_rules(),
        config_drive.list_rules(),
        console_auth_tokens.list_rules(),
        console_output.list_rules(),
        consoles.list_rules(),
        create_backup.list_rules(),
        deferred_delete.list_rules(),
        evacuate.list_rules(),
        extended_availability_zone.list_rules(),
        extended_server_attributes.list_rules(),
        extended_status.list_rules(),
        extended_volumes.list_rules(),
        extension_info.list_rules(),
        extensions.list_rules(),
        fixed_ips.list_rules(),
        flavor_access.list_rules(),
        flavor_extra_specs.list_rules(),
        flavor_manage.list_rules(),
        flavor_rxtx.list_rules(),
        flavors.list_rules(),
        floating_ip_dns.list_rules(),
        floating_ip_pools.list_rules(),
        floating_ips.list_rules(),
        floating_ips_bulk.list_rules(),
        fping.list_rules(),
        hide_server_addresses.list_rules(),
        hosts.list_rules(),
        hypervisors.list_rules(),
        image_metadata.list_rules(),
        image_size.list_rules(),
        images.list_rules(),
        instance_actions.list_rules(),
        instance_usage_audit_log.list_rules(),
        ips.list_rules(),
        keypairs.list_rules(),
        limits.list_rules(),
        lock_server.list_rules(),
        migrate_server.list_rules(),
        migrations.list_rules(),
        multinic.list_rules(),
        multiple_create.list_rules(),
        networks.list_rules(),
        networks_associate.list_rules(),
        pause_server.list_rules(),
        pci.list_rules(),
        quota_class_sets.list_rules(),
        quota_sets.list_rules(),
        remote_consoles.list_rules(),
        rescue.list_rules(),
        scheduler_hints.list_rules(),
        security_group_default_rules.list_rules(),
        security_groups.list_rules(),
        server_diagnostics.list_rules(),
        server_external_events.list_rules(),
        server_groups.list_rules(),
        server_metadata.list_rules(),
        server_password.list_rules(),
        server_tags.list_rules(),
        server_usage.list_rules(),
        servers.list_rules(),
        servers_migrations.list_rules(),
        services.list_rules(),
        shelve.list_rules(),
        simple_tenant_usage.list_rules(),
        suspend_server.list_rules(),
        tenant_networks.list_rules(),
        used_limits.list_rules(),
        user_data.list_rules(),
        versions.list_rules(),
        virtual_interfaces.list_rules(),
        volumes.list_rules(),
        volumes_attachments.list_rules(),
        wstvms.list_rules(),
        wsthost.list_rules(),
        cpu_priority.list_rules(),
        ics_hosts.list_rules(),
        clusters.list_rules(),
        drs.list_rules(),
        cpu_qos.list_rules(),
        mem_priority.list_rules(),
        disk_qos.list_rules(),
        hostnic.list_rules(),
        ics_datastore.list_rules(),
        panick_policy.list_rules(),
        ics_vm.list_rules(),
        monitorstatus.list_rules(),
        mem_snapshots.list_rules()

    )
