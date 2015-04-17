#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    description = module.params['description']
    major = module.params['major']
    minor = module.params['minor']
    name = module.params['name']
    state = module.params['state']

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
        os = theforeman.search_operatingsystem(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get operatingsystem: {0}'.format(e.message))

    data['description'] = description
    data['major'] = major
    data['minor'] = minor

    if not os and state == 'present':
        try:
            theforeman.create_operatingsystem(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create operatingsystem: {0}'.format(e.message))

    if os:
        if state == 'absent':
            try:
                theforeman.delete_operatingsystem(id=os.get('id'))
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not delete operatingsystem: {0}'.format(e.message))

        if not all(data[key] == os.get(key, data[key]) for key in data):
            try:
                theforeman.update_operatingsystem(id=os.get('id'), data=data)
                return True
            except ForemanError as e:
                module.fail_json(msg='Could not update operatingsystem: {0}'.format(e.message))

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            description=dict(type='str', required=False),
            major=dict(type='str', required=True),
            minor=dict(type='str', required=False),
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            foreman_host=dict(type='str', default='127.0.0.1'),
            foreman_port=dict(type='str', default='443'),
            foreman_user=dict(type='str', required=True),
            foreman_pass=dict(type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed = ensure(module)
    module.exit_json(changed=changed, name=module.params['name'])

# import module snippets
from ansible.module_utils.basic import *

main()
