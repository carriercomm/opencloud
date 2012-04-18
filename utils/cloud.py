#!/usr/bin/env python
#    Copyright 2012 OpenCloud Project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import ScriptDeployment
import libcloud.security
import logging
import config

libcloud.security.VERIFY_SSL_CERT = config.LIBCLOUD_VERIFY_CERTS

def _get_connection(provider=None, id=None, key=None):
    """
    Gets a libcloud connection to the specified provider
    
    :param provider: Name of provider (i.e. ec2)
    :param id: Provider ID 
    :param key: Provider Key
    
    """
    log = logging.getLogger(__name__)
    providers = {
        'ec2': Provider.EC2,
        'us-east-1': Provider.EC2_US_EAST,
        'us-west-1': Provider.EC2_US_WEST,
        'us-west-2': Provider.EC2_US_WEST_OREGON,
        'eu-west-1': Provider.EC2_EU_WEST,
        'rackspace': Provider.RACKSPACE,
        'rackspace_uk': Provider.RACKSPACE_UK,
        'dfw': Provider.RACKSPACE,
    }
    driver = get_driver(providers[provider.lower()])
    conn = driver(id, key)
    return conn
    
def get_nodes(provider=None, id=None, key=None, node_ids=None):
    """
    List all nodes for the specified provider
    
    :param provider: Name of provider (i.e. ec2)
    :param id: Provider ID 
    :param key: Provider Key
    :param node_ids: List of node IDs to filter
    
    :rtype: `list` of nodes
    
    """
    log = logging.getLogger(__name__)
    log.debug('Getting list of nodes for {0}'.format(provider))
    conn = _get_connection(provider, id, key)
    return conn.list_nodes(node_ids)
    
def reboot_node(provider=None, id=None, key=None, node_id=None):
    """
    Reboots an instance

    :param provider: Name of provider (i.e. ec2)
    :param id: Provider ID 
    :param key: Provider Key
    :param node_id: ID of the node to restart
    
    """
    log = logging.getLogger(__name__)
    log.debug('Restarting instance {0}'.format(node_id))
    node = get_nodes(provider, id, key, [node_id])[0]
    return node.reboot()

    