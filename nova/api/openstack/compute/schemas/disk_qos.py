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

diskqos = {
    'type': 'object',
    'properties': {
        'vmid': parameter_types.server_id,
        'disk_qos': {
            'type': 'object',
            'properties': {
                'enabled': parameter_types.boolean,
                'readBps': {
                    'type': 'string', 'maxLength': 255,
                },
                'writeBps': {
                    'type': 'string', 'maxLength': 255,
                },
                'readIops':{
                    'type': 'string', 'maxLength': 255,
                },
                'writeIops':{
                    'type': 'string', 'maxLength': 255,
                },
                'totalBps': {
                    'type': 'string', 'maxLength': 255,
                },
                'totalIops':{
                    'type': 'string', 'maxLength': 255,
                },
            },
        },
    },
    'required': ['vmid', 'disk_qos'],
    'additionalProperties': False
}
