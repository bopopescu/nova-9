# Copyright 2017 Inspur Corporation
# All Rights Reserved.

from nova.api.validation import parameter_types


setdrs = {
    'type': 'object',
    'properties': {
        'value': parameter_types.boolean,
    },
    'required': ['value'],
    'additionalProperties': False,
}


setdpm = {
    'type': 'object',
    'properties': {
        'value': parameter_types.boolean,
    },
    'required': ['value'],
    'additionalProperties': False,
}
