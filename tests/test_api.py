from AnsibleApi.interface import InterFace

aaa = {
    "inventory": "/etc/ansible/hosts"
}

f = InterFace(
    inventory="/etc/ansible/hosts",
    # skip_tags=["named"],
    limit="all",
    extra_vars={"username": 'chkconfigdeqwdqew'}
)
f.run_play(['~/github/AnsibleApi/tests/test.yml'])