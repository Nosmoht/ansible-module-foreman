#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from foreman.foreman import *

    foremanclient_found = True
except ImportError:
    foremanclient_found = False


def ensure(module):
    updateable_keys = ['url']

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

    data['url'] = url

    if not smart_proxy and state == 'present':
        try:
            smart_proxy = theforeman.create_smart_proxy(data=data)
            return True, smart_proxy
        except ForemanError as e:
            module.fail_json(msg='Could not create smart proxy: {0}'.format(e.message))

    if smart_proxy:
        if state == 'absent':
            try:
                smart_proxy = theforeman.delete_smart_proxy(id=smart_proxy.get('id'))
                return True, smart_proxy
            except:
                module.fail_json(msg='Could not delete smart proxy: {0}'.format(e.message))

        if not all(data[key] == smart_proxy[key] for key in updateable_keys):
            try:
                smart_proxy = theforeman.update_smart_proxy(id=smart_proxy.get('id'), data=data)
                return True, smart_proxy
            except ForemanError as e:
                module.fail_json(msg='Could not update smart proxy: {0}'.format(e.message))
    return False, smart_proxy


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

    changed, smart_proxy = ensure(module)
    module.exit_json(changed=changed, smart_proxy=smart_proxy)

# import module snippets
from ansible.module_utils.basic import *

main()
