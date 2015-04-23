#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    name = module.params['name']
    url = module.params['url']
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
        smart_proxy = theforeman.search_smart_proxy(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get smart proxy: {0}'.format(e.message))

    if not smart_proxy and state == 'present':
        data['url'] = url
        try:
            theforeman.create_smart_proxy(data=data)
            return True
        except ForemanError as e:
            module.fail_json(msg='Could not create smart proxy: {0}'.format(e.message))

    if smart_proxy:
        if state == 'absent':
            try:
                theforeman.delete_smart_proxy(id=smart_proxy.get('id'))
                return True
            except:
                module.fail_json(msg='Could not delete smart proxy: {0}'.format(e.message))

    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            url=dict(type='str', required=False),
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
