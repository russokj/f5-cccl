#!/usr/bin/env python
# Copyright 2017 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from f5_cccl.utils.resource_merge import merge

def test_scalars():
    """ Test simple scalar merging (replacing) """

    test_data = [
        # desired, existing, merged
        (4, 3, 4),
        ('a', 'b', 'a'),
        (True, False, True)
    ]
    for test in test_data:
        desired = test[0]
        existing = test[1]
        expected = test[2]
        assert merge(existing, desired) == expected


def test_simple_arrays():
    """ Test simple list merging (replacing) """

    test_data = [
        # desired, existing, merged
        ([], [], []),
        ([], [1], [1]),
        ([1], [], [1]),
        ([1], [2], [1, 2]),
        ([2], [1], [1, 2]),
        ([1, 2], [1], [1, 2]),
        ([1], [1, 2], [1, 2]),
        ([1, 3], [1, 2], [1, 2, 3]),
        (['apple', 'orange'], ['apple', 'pear'], ['apple', 'pear', 'orange'])
    ]
    for test in test_data:
        desired = test[0]
        existing = test[1]
        expected = test[2]
        assert merge(existing, desired).sort() == expected.sort()


def test_simple_dict():
    """ Test simple dictionary merging """

    test_data = [
        # desired, existing, merged
        ({}, {'a': 1}, {'a': 1}),
        ({'a': 1}, {}, {'a': 1}),
        ({'a': 1}, {'a': 2}, {'a': 1}),
        ({'a': 1}, {'b': 2}, {'a': 1, 'b': 2}),
        ({'a': 1, 'b': 3}, {'b': 2}, {'a': 1, 'b': 3}),
        ({'a': 1, 'b': 2}, {'c': 3, 'd': 4}, {'a': 1, 'b': 2, 'c': 3, 'd': 4})
    ]
    for test in test_data:
        desired = test[0]
        existing = test[1]
        expected = test[2]
        assert merge(existing, desired) == expected


def test_list_of_named_dict():
    """ Test merge lists of named dictionary objects

        This is unique for Big-IP resources that are
        lists of named objects
    """

    test_data = [
        # desired, existing, merged
        ([], [], []),
        ([], [{'name': 'resource-a', 'value': 1}], [{'name': 'resource-a', 'value': 1}]),
        ([{'name': 'resource-a', 'value': 1}], [], [{'name': 'resource-a', 'value': 1}]),
        ([{'name': 'resource-a', 'value': 1}], [{'name': 'resource-a', 'value': 3}], [{'name': 'resource-a', 'value': 1}]),
        ([{'name': 'resource-a', 'value1': 1, 'value2': 2}],
         [{'name': 'resource-a', 'value2': 0, 'value3': 3}],
         [{'name': 'resource-a', 'value1': 1, 'value2': 2, 'value3': 3}]),
        ([{'name': 'resource-a', 'value1': 1, 'value2': 2}, {'name': 'resource-b', 'valueB': 'b'}],
         [{'name': 'resource-a', 'value2': 0, 'value3': 3}, {'name': 'resource-c', 'valueC': 'c'}],
         [{'name': 'resource-a', 'value1': 1, 'value2': 2, 'value3': 3},
          {'name': 'resource-b', 'valueB': 'b'}, {'name': 'resource-c', 'valueC': 'c'}])
    ]
    for test in test_data:
        desired = test[0]
        existing = test[1]
        expected = test[2]
        assert merge(existing, desired) == expected


def test_sample_resource():
    """ Test merge lists of named dictionary objects

        This is unique for Big-IP resources that are
        lists of named objects
    """

    desired = {
        'destination': '/test/172.16.3.59%0:80',
        'name': u'ingress_172-16-3-59_80',
        'rules': [],
        'vlansDisabled': True,
        'enabled': True,
        'sourceAddressTranslation': {
            u'type': u'automap'
        },
        'partition': u'test',
        'source': '0.0.0.0%0/0',
        'profiles': [
            {
                u'partition': u'Common',
                u'name': u'http',
                u'context': u'all'
            },
            {
                u'partition': u'Common',
                u'name': u'tcp',
                u'context': u'all'
            }
        ],
        'connectionLimit': 0,
        'ipProtocol': u'tcp',
        'vlans': [],
        'policies': [
            {
                u'partition': u'test',
                u'name': u'ingress_172-16-3-59_80'
            }
        ]
    }

    existing = {
        'destination': '/test/172.16.3.59%0:80',
        'name': u'ingress_172-16-3-59_80',
        'rules': [],
        'vlansDisabled': False, # This should change
        'enabled': True,
        'sourceAddressTranslation': {
            u'type': u'snat' # This should change
        },
        'partition': u'test',
        'source': '0.0.0.0%0/0',
        'profiles': [
            {
                'partition': u'Common',
                'name': u'html',
                'context': u'all'
            },
            { # This should be kept
                'partition': u'Common',
                'name': u'http',
                'context': u'all'
            },
            {
                'partition': u'Common',
                'name': u'tcp',
                'context': u'all'
            }
        ],
        'connectionLimit': 1, # This should change
        'ipProtocol': u'tcp',
        'vlans': [
            { # This should be added
                'name': 'vlan',
                'a': '1',
                'b': '2'
            }
        ],
        'policies': []  # This should be replaced
    }
    
    expected = {
        'destination': '/test/172.16.3.59%0:80',
        'name': u'ingress_172-16-3-59_80',
        'rules': [],
        'vlansDisabled': True,
        'enabled': True,
        'sourceAddressTranslation': {
            u'type': u'automap'
        },
        'partition': u'test',
        'source': '0.0.0.0%0/0',
        'profiles': [
            {
                'partition': u'Common',
                'name': u'html',
                'context': u'all'
            },
            {
                'partition': u'Common',
                'name': u'http',
                'context': u'all'
            },
            {
                'partition': u'Common',
                'name': u'tcp',
                'context': u'all'
            }
        ],
        'connectionLimit': 0,
        'ipProtocol': u'tcp',
        'vlans': [
            {
                'name': 'vlan',
                'a': '1',
                'b': '2'
            }
        ],
        'policies': [
            {
                u'partition': u'test',
                u'name': u'ingress_172-16-3-59_80'
            }
        ]
    }
    
    assert merge(existing, desired) == expected


def test_sample_resource2():
    """ Test merge lists of named dictionary objects

        This is unique for Big-IP resources that are
        lists of named objects
    """

    desired = {'destination': '/test/172.16.3.60%0:80', 'name': u'ingress_172-16-3-60_80', 'rules': [], 'vlansDisabled': True, 'enabled': True, 'sourceAddressTranslation': {u'type': u'automap'}, 'partition': u'test', 'source': '0.0.0.0%0/0', 'profiles': [{u'partition': u'Common', u'name': u'http', u'context': u'all'}, {u'partition': u'Common', u'name': u'tcp', u'context': u'all'}], 'connectionLimit': 0, 'ipProtocol': u'tcp', 'vlans': [], 'policies': [{u'partition': u'test', u'name': u'ingress_172-16-3-60_80'}]}
    existing = {'destination': '/test/172.16.3.60%0:80', 'name': u'ingress_172-16-3-60_80', 'rules': [], 'vlansDisabled': True, 'enabled': True, 'sourceAddressTranslation': {u'type': u'automap'}, 'partition': u'test', 'source': '0.0.0.0%0/0', 'profiles': [{'partition': u'Common', 'name': u'html', 'context': u'all'}, {'partition': u'Common', 'name': u'http', 'context': u'all'}, {'partition': u'Common', 'name': u'tcp', 'context': u'all'}], 'connectionLimit': 0, 'ipProtocol': u'tcp', 'vlans': [], 'policies': []}
    expected = {'destination': '/test/172.16.3.60%0:80', 'name': u'ingress_172-16-3-60_80', 'rules': [], 'vlansDisabled': True, 'enabled': True, 'sourceAddressTranslation': {u'type': u'automap'}, 'partition': u'test', 'source': '0.0.0.0%0/0', 'profiles': [{u'partition': u'Common', u'name': u'html', u'context': u'all'}, {u'partition': u'Common', u'name': u'http', u'context': u'all'}, {u'partition': u'Common', u'name': u'tcp', u'context': u'all'}], 'connectionLimit': 0, 'ipProtocol': u'tcp', 'vlans': [], 'policies': [{u'partition': u'test', u'name': u'ingress_172-16-3-60_80'}]}

    assert merge(existing, desired) == expected
