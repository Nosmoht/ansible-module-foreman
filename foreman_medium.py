#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True

def ensure(module):
    name = module.params['name']
    path = module.params['path']
    state = module.params['state']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']
    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)
    data = {}
    data['name'] = name

    try:
        medium = theforeman.search_medium(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get medium: {0}'.format(e.message))

    if not medium and state == 'present':
        try:
            theforeman.create_medium(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create medium: {0}'.format(e.message))

    if medium and state == 'absent':
        try:
            theforeman.delete_medium(id=medium.get('id'))
            return True
        except ForemanError as e:
            module.fail_json('Could not delete medium: {0}'.format(e.message))

    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            path=dict(type='str', required=False),
            state=dict(Type='str', Default='present', choices=['present', 'absent']),
            foreman_host=dict(Type='str', Default='127.0.0.1'),
            foreman_port=dict(Type='str', Default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *
main()
