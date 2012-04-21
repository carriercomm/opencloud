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
from flask import Blueprint
from flask import request, render_template, jsonify, g, flash, redirect, url_for, session, current_app
from flaskext.login import login_required
import messages
from utils import cloud

bp = dashboard_blueprint = Blueprint('dashboard', __name__)

def get_provider_info(provider=None):
    data = {}
    org = request.args.get('organization', session.get('default_organization'))
    org_data = current_app.config.get('APP_CONFIG').get('organizations').get(org)
    provider_id = None
    provider_key = None
    if org_data:
        provider_id = org_data.get('provider_id')
        provider_key = org_data.get('provider_key')
    data.update(
        provider = provider,
        provider_id = provider_id,
        provider_key = provider_key
    )
    return data
    
@bp.route('/')    
@bp.route('/<region>')
@login_required
def index(region=None):
    regions = []
    org_data = current_app.config.get('APP_CONFIG').get('organizations').get(session.get('default_organization'))
    if org_data:
        provider = org_data.get('provider')
        regions = current_app.config.get('REGIONS').get(provider)
    ctx = {
        'provider': provider,
        'regions': regions,
        'region': region,
    }
    return render_template('dashboard/index.html', **ctx)
    
@bp.route('/nodes/<provider>/<region>/')
@login_required
def nodes(provider=None, region=None):
    org = request.args.get('organization', session.get('default_organization'))
    nodes = None
    provider_info = get_provider_info(provider)
    if provider_info.get('provider'):
        provider_id = provider_info.get('provider_id')
        provider_key = provider_info.get('provider_key')
        nodes = cloud.get_nodes(provider, region, provider_id, provider_key)
    ctx = {
        'provider': provider,
        'region': region,
        'nodes': nodes,
    }
    return render_template('dashboard/_nodes.html', **ctx)

@bp.route('/nodes/<provider>/<region>/<node_id>/reboot')
@login_required
def node_reboot(provider=None, region=None, node_id=None):
    org = request.args.get('organization', session.get('default_organization'))
    provider_info = get_provider_info(provider)
    if provider_info.get('provider'):
        provider_id = provider_info.get('provider_id')
        provider_key = provider_info.get('provider_key')
        cloud.reboot_node(provider, region, provider_id, provider_key, node_id)
        flash(messages.INSTANCE_REBOOTED)
    return redirect(url_for('dashboard.index', region=region))

@bp.route('/nodes/<provider>/<region>/<node_id>/stop')
@login_required
def node_stop(provider=None, region=None, node_id=None):
    org = request.args.get('organization', session.get('default_organization'))
    provider_info = get_provider_info(provider)
    if provider_info.get('provider'):
        provider_id = provider_info.get('provider_id')
        provider_key = provider_info.get('provider_key')
        if cloud.stop_node(provider, region, provider_id, provider_key, node_id):
            flash(messages.INSTANCE_STOPPED)
    return redirect(url_for('dashboard.index', region=region))
 
@bp.route('/nodes/<provider>/<region>/<node_id>/destroy')
@login_required
def node_destroy(provider=None, region=None, node_id=None):
    org = request.args.get('organization', session.get('default_organization'))
    provider_info = get_provider_info(provider)
    if provider_info.get('provider'):
        provider_id = provider_info.get('provider_id')
        provider_key = provider_info.get('provider_key')
        cloud.destroy_node(provider, region, provider_id, provider_key, node_id)
        flash(messages.INSTANCE_DESTROYED)
    return redirect(url_for('dashboard.index', region=region))

@bp.route('/nodes/<provider>/<region>/launch')
@login_required
def node_launch(provider=None, region=None):
    org = request.args.get('organization', session.get('default_organization'))
    regions = None
    nodes = None
    provider_info = get_provider_info(provider)
    if provider_info.get('provider'):
        provider_id = provider_info.get('provider_id')
        provider_key = provider_info.get('provider_key')
        regions = current_app.config.get('REGIONS').get(provider)
    ctx = {
        'provider': provider,
        'regions': regions,
        'images': cloud.get_images(provider, provider_id, provider_key),
        'sizes': cloud.get_sizes(provider, provider_id, provider_key),
    }
    return render_template('dashboard/_launch_server.html', **ctx)