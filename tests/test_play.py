import json
import shutil

import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.vars.manager import VariableManager
from ansible import context

from AnsibleApi import CallBack

host_path = "/etc/ansible/hosts"
play_book_path = "test.yml"

# 初始化 context 参数
context.CLIARGS = ImmutableDict(
    connection='smart',
    # module_path=[],
    forks=10,
    become=False,
    become_method="sudo",
    become_user=None,
    diff=False,
    verbosity=6,
    check=False,
    syntax=False,
    start_at_task=None,
    tags=[],
    skip_tags=[]
)

# 全局加载器
loader = DataLoader()

# 初始化inventory
inventory = InventoryManager(loader=loader, sources=host_path)
inventory.subset("188.131.128.180")

# 初始化 variable 管理器，需要传入的 extra_vars 需从此插入
variable_manager = VariableManager(loader=loader, inventory=inventory)
variable_manager.extra_vars.update({
    "username": "chkconfig"
})
# extra_vars={"username": "chkchon"}

# callback
result_callback = CallBack()

# 初始化 任务队列
tmq = TaskQueueManager(
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords={},
    stdout_callback=result_callback
)

# 初始化 playbook
playbook_executor = PlaybookExecutor(
    playbooks=[play_book_path],
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords={}
)

code = playbook_executor.run()



