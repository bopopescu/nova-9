# Copyright 2014 NEC Corporation.  All rights reserved.
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


from nova.api.validation import parameter_types

mount = {
    'type': 'object',
    'properties': {
        'vmid': parameter_types.server_id,
        'isoid': parameter_types.image_id,
    },
    'required': ['vmid', 'isoid'],
    'additionalProperties': False
}

unmount = {
    'type': 'object',
    'properties': {
        'vmid': parameter_types.server_id,
    },
    'required': ['vmid'],
    'additionalProperties': False
}

attach_usb = {
    'type': 'object',
    'properties': {
        'bus': parameter_types.name,
        'device': parameter_types.name,
        'releaseAfterPowerOff': parameter_types.boolean
    },
    'required': ['bus', 'device', 'releaseAfterPowerOff'],
    'additionalProperties': False
}
