# import ansible packages
from ansible.parsing.dataloader import DataLoader
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
from ansible.vars.manager import VariableManager
from ansible import context
# import UserCallBack modules
from AnsibleApi import CallBack
from ansible.utils.ssh_functions import set_default_transport


class PlayBookExec(PlaybookExecutor):
    """
    : 重写 PlaybookExecutor 类以实现 Callback 插入
    """
    def __init__(self,
                 playbooks,
                 inventory,
                 variable_manager,
                 loader,
                 passwords,
                 callback=None):
        self._playbooks = playbooks
        self._inventory = inventory
        self._variable_manager = variable_manager
        self._loader = loader
        self.passwords = passwords
        self._unreachable_hosts = dict()

        if context.CLIARGS.get('listhosts') or context.CLIARGS.get('listtasks') or \
                context.CLIARGS.get('listtags') or context.CLIARGS.get('syntax'):
            self._tqm = None
        else:
            self._tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                passwords=self.passwords,
                forks=context.CLIARGS.get('forks'),
                stdout_callback=callback
            )

        set_default_transport()


class InterFace(object):
    """
    : Ansible API 调用接口
    : 接收类似ansible-playbook参数:
    :   param limit     : str, split with ``,``
    :   param tags      : list
    :   param skip_tags : list
    :   extra-vars      : dict
    """

    def __init__(self, **kwargs):
        # 用户操作常用参数
        # 必须参数
        self.inventory = kwargs["inventory"]
        # 非必须参数
        self.limit = kwargs.get("limit", "all")
        self.tags = kwargs.get("tags", [])
        self.skip_tags = kwargs.get("skip_tags", [])
        self.extra_vars = kwargs.get("extra_vars", {})
        # 非常用参数
        self.passwords = kwargs.get("passwords", {})
        self.module_path = kwargs.get("module_path", [])
        self.forks = kwargs.get("forks", 20)
        self.connection = kwargs.get("connection", "smart")
        self.become_method = kwargs.get("become_method", "sudo")
        self.become_user = kwargs.get("become_user", None)
        self.become = kwargs.get("become", False)
        self.verbosity = kwargs.get("verbosity", 0)
        self.start_at_task = kwargs.get("start_at_task", None)
        self.diff = kwargs.get("diff", False)
        self.check = kwargs.get("check", False)
        self.syntax = kwargs.get("syntax", False)

    def _ctx_cli(self):
        context.CLIARGS = ImmutableDict(
            connection=self.connection,
            module_path=self.module_path,
            forks=self.forks,
            become=self.become,
            become_method=self.become_method,
            become_user=self.become_user,
            diff=self.diff,
            verbosity=self.verbosity,
            check=self.check,
            syntax=self.syntax,
            start_at_task=self.start_at_task,
            tags=self.tags,
            skip_tags=self.skip_tags
        )

    def _task_queue(self,
                    inventory,
                    variable_manager,
                    loader,
                    callback):
        task_queue = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=self.passwords,
            stdout_callback=callback
        )
        return task_queue

    def _playbook_executor(self,
                           playbooks,
                           inventory,
                           variable_manager,
                           loader,
                           callback=None):
        pbex = PlayBookExec(
            playbooks=playbooks,
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=self.passwords,
            callback=callback
        )
        # if callback:
        #     pbex._tqm._stdout_callback = callback
        return pbex

    def run_play(self, play_book_path: list):
        loader = DataLoader()
        self._ctx_cli()
        inventory = InventoryManager(loader=loader, sources=self.inventory)
        inventory.subset(self.limit)
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        variable_manager.extra_vars.update(self.extra_vars)
        callback = CallBack()
        task_queue = self._task_queue(
            inventory,
            variable_manager,
            loader,
            callback
        )
        playbook_executor = self._playbook_executor(
            play_book_path,
            inventory,
            variable_manager,
            loader,
            callback
        )
        code = playbook_executor.run()
        return code