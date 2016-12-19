#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Ansible module to manage Foreman operating system resources.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: foreman_image
short_description:
- Manage Foreman images using Foreman API v2.
description:
- Create, update and and delete Foreman images using Foreman API v2
options:
  name:
    description: Image name as used in Foreman
    required: true
  state:
    description: image state
    required: false
    default: 'present'
    choices: ['present', 'absent']
  uuid:
  operatingsystem:
    description: Operatingsystem used on the image
    required: True
  architecture:
    description: Architecture the image is for
    required: True
  uuid:
    description: UUID of the image
    required: True
  user:
    description: User used to log into the image
    required: False
    default: root
  foreman_host:
    description: Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description: Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description: Username to be used to authenticate on Foreman
    required: true
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
  foreman_ssl:
    description: Enable SSL when connecting to Foreman API
    required: false
    default: true
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
version_added: "2.0"
author: "Guido Günther <agx@sigxcpu.org>"
'''

EXAMPLES = '''
- name: Ensure Debian Jessie Image
  foreman_image:
    name: Debian Jessie Minimal
    architecture: x86_64
    operatingsystem: DebianJessie
    uuid: /path/to/image
    state: present
    foreman_host: 127.0.0.1
    foreman_port: 443
    foreman_user: admin
    foreman_pass: secret
'''

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def get_resources(resource_type, resource_func, resource_name, search_field='name'):
    if not resource_name:
        return None
    search_data = dict()
    search_data[search_field] = resource_name
    try:
        resource = resource_func(data=search_data)
        if not resource:
            module.fail_json(
                msg='Could not find resource type {resource_type} specified as {name}'.format(
                    resource_type=resource_type, name=resource_name))
    except ForemanError as e:
        module.fail_json(msg='Could not search resource type {resource_type} specified as {name}: {error}'.format(
            resource_type=resource_type, name=resource_name, error=e.message))
    return resource


def ensure():
    name = module.params['name']
    compute_resource_name = module.params['compute_resource']
    state = module.params['state']

    data = dict(name=name)

    try:
        compute_resource = theforeman.search_compute_resource(data=dict(name=compute_resource_name))
    except ForemanError as e:
        module.fail_json(msg='Could not find compute resource {0}: {1}'.format(compute_resource_name, e.message))

    if not compute_resource:
        module.fail_json(msg='Could not find compute resource {0}'.format(compute_resource_name))

    cid = compute_resource['id']
    try:
        images = theforeman.get_compute_resource_images(compute_resource['id'])
        for i in images:
            if i['name'] == name:
                image = i
                break
        else:
            image = None
    except ForemanError as e:
        module.fail_json(msg='Could not get images: {0}'.format(e.message))

    if state == 'absent':
        if image:
            try:
                image = theforeman.delete_compute_resource_image(cid, image.get('id'))
                return True, image
            except ForemanError as e:
                module.fail_json(msg='Could not delete image: {0}'.format(e.message))

        return False, image

    data['compute_resource_id'] = cid
    data['uuid'] = module.params['uuid']
    data['username'] = module.params['user']
    if module.params['password']:
        data['password'] = module.params['password']
    data['architecture_id'] = get_resources(resource_type='architecture',
                                            resource_func=theforeman.search_architecture,
                                            resource_name=module.params['architecture'])['id']
    data['operatingsystem_id'] = get_resources(resource_type='operatingsystem',
                                               resource_func=theforeman.search_operatingsystem,
                                               resource_name=module.params['operatingsystem'],
                                               search_field='title')['id']

    if not image:
        try:
            image = theforeman.create_compute_resource_image(compute_resource_id=cid,
                                                             data=data)
            return True, image
        except ForemanError as e:
            module.fail_json(msg='Could not create image: {0}'.format(e.message))
    else:
        data['id'] = image['id']

    if not all(data[key] == image.get(key, data[key]) for key in data.keys()):
        try:
            new_data = dict(compute_resource_id=cid, id=image['id'], image=data)
            image = theforeman.update_compute_resource_image(compute_resource_id=cid,
                                                             data=new_data)
            return True, image
        except ForemanError as e:
            module.fail_json(msg='Could not update image: {0}'.format(e.message))

    return False, image


def main():
    global module
    global theforeman

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            compute_resource=dict(type='str', required=True),
            architecture=dict(type='str', required=True),
            operatingsystem=dict(operatingsystem='str', required=True),
            uuid=dict(type='str', required=True),
            user=dict(type='str', default='root'),
            password=dict(type='str', default=None, no_log=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True, no_log=True),
            foreman_ssl=dict(type='bool', default=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    foreman_ssl = module.params['foreman_ssl']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass,
                         ssl=foreman_ssl)

    changed, image = ensure()
    module.exit_json(changed=changed, image=image)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
