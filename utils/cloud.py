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
from flaskext.cache import Cache
import logging
import config

libcloud.security.VERIFY_SSL_CERT = config.LIBCLOUD_VERIFY_CERTS

app = config.create_app()
cache = Cache(app)

def _get_connection(provider=None, region=None, id=None, key=None):
    """
    Gets a libcloud connection to the specified provider
    
    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key
    
    """
    log = logging.getLogger(__name__)
    regions = {
        'ec2': Provider.EC2,
        'us-east-1': Provider.EC2_US_EAST,
        'us-west-1': Provider.EC2_US_WEST,
        'us-west-2': Provider.EC2_US_WEST_OREGON,
        'eu-west-1': Provider.EC2_EU_WEST,
        'rackspace': Provider.RACKSPACE,
        'rackspace_uk': Provider.RACKSPACE_UK,
        'dfw': Provider.RACKSPACE,
    }
    driver = get_driver(regions[region.lower()])
    conn = driver(id, key)
    return conn
    
def get_nodes(provider=None, region=None, id=None, key=None, node_ids=None):
    """
    List all nodes for the specified provider
    
    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key
    :param node_ids: List of node IDs to filter
    
    :rtype: `list` of nodes
    
    """
    log = logging.getLogger(__name__)
    log.debug('Getting list of nodes for {0}'.format(provider))
    nodes = None
    if node_ids and not isinstance(node_ids, list):
        nodes_ids = [node_ids]
    conn = _get_connection(provider, region, id, key)
    if provider == 'ec2':
        nodes = conn.list_nodes(node_ids)
    else:
        nodes = conn.list_nodes()
    return nodes
    
def reboot_node(provider=None, region=None, id=None, key=None, node_id=None):
    """
    Reboots an instance

    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key
    :param node_id: ID of the node to restart
    
    """
    log = logging.getLogger(__name__)
    log.debug('Restarting instance {0}'.format(node_id))
    node = get_nodes(provider, region, id, key, [node_id])[0]
    ret_val = None
    # check if node is stopped ; run start instead of reboot
    if node.state == 4:
        ret_val = node.driver.ex_start_node(node)
    else:
        ret_val = node.reboot()
    return ret_val

def stop_node(provider=None, region=None, id=None, key=None, node_id=None):
    """
    Stops an instance

    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key
    :param node_id: ID of the node to restart

    """
    log = logging.getLogger(__name__)
    log.debug('Stopping instance {0}'.format(node_id))
    node = get_nodes(provider, region, id, key, [node_id])[0]
    ret_val = False
    # only ec2 can 'stop' nodes
    ret_val = node.driver.ex_stop_node(node)
    return ret_val

def destroy_node(provider=None, region=None, id=None, key=None, node_id=None):
    """
    Destroys an instance

    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key
    :param node_id: ID of the node to restart

    """
    log = logging.getLogger(__name__)
    log.debug('Destroying instance {0}'.format(node_id))
    node = get_nodes(provider, region, id, key, [node_id])[0]
    return node.destroy()

@cache.memoize(3600)
def _get_ec2_images(region=None, id=None, key=None):
    """
    Gets all Amazon EC2 images
    This is cached on app startup
    
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key

    :rtype: `list` of images

    """
    conn = _get_connection('ec2', region, id, key)
    images = []
    [images.append({'name': x.name, 'id': x.id}) for x in conn.list_images()]
    return images

@cache.memoize(3600)
def _get_rackspace_images(region=None, id=None, key=None):
    """
    Gets all Rackspace images
    This is cached on app startup

    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key

    :rtype: `list` of images

    """
    conn = _get_connection('rackspace', region, id, key)
    images = []
    [images.append({'name': x.name, 'id': x.id}) for x in conn.list_images()]
    return images

def get_images(provider=None, region=None, id=None, key=None):
    """
    List all images for the specified provider

    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key

    :rtype: `list` of images

    """
    log = logging.getLogger(__name__)
    log.debug('Getting list of images for {0}'.format(provider))
    images = {
        'ec2': _get_ec2_images,
        'rackspace': _get_rackspace_images,
    }
    return images[provider](region, id, key)

def get_sizes(provider=None, region=None, id=None, key=None):
    """
    List all sizes for the specified provider

    :param provider: Name of provider (i.e. ec2)
    :param region: Name of region
    :param id: Provider ID 
    :param key: Provider Key

    :rtype: `list` of sizes

    """
    log = logging.getLogger(__name__)
    log.debug('Getting list of sizes for {0}'.format(provider))
    conn = _get_connection(provider, region, id, key)
    return conn.list_sizes()
