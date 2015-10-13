#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    name = module.params['name']
    path = module.params['path']
    state = module.params['state']
    os_family = module.params['os_family']

    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {'name': name}

    try:
        medium = theforeman.search_medium(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get medium: {0}'.format(e.message))

    data['path'] = path
    data['os_family'] = os_family

    if not medium and state == 'present':
        try:
            medium = theforeman.create_medium(data=data)
            return True, medium
        except ForemanError as e:
            module.fail_json(msg='Could not create medium: {0}'.format(e.message))

    if medium:
        if state == 'absent':
            try:
                medium = theforeman.delete_medium(id=medium.get('id'))
                return True, medium
            except ForemanError as e:
                module.fail_json('Could not delete medium: {0}'.format(e.message))
        if medium.get('path') != path or medium.get('os_family') != os_family:
            try:
                medium = theforeman.update_medium(id=medium.get('id'), data=data)
                return True, medium
            except ForemanError as e:
                module.fail_json(msg='Could not update medium: {0}'.format(e.message))

    return False, medium


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            path=dict(type='str', required=False),
            os_family=dict(type='str', required=False),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, medium = ensure(module)
    module.exit_json(changed=changed, medium=medium)

# import module snippets
from ansible.module_utils.basic import *

main()
