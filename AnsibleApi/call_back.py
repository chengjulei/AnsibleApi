import json

from ansible.plugins.callback.default import CallbackModule
from ansible.plugins.callback import CallbackBase
from ansible.utils.display import Display


class CallBack(CallbackBase):
    """
    : 继承 CallbackBase 类
    : 重写需求模块
    """

    def __init__(self, display=None, options=None, *args, **kwargs):
        super(CallBack, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        print(dir(self))

    # def v2_runner_on_unreachable(self, result):
    #     host = result._host
    #     self.host_unreachable[host.get_name()] = result
    #
    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        print(dir(result))
        host = result._host
        self.host_ok[host.get_name()] = result
        # print(json.dumps({host.name: result._result}, indent=4))
        print(self._dump_results(result._result))

    # def v2_runner_on_failed(self, result, *args, **kwargs):
    #     host = result._host
    #     self.host_failed[host.get_name()] = result
    #     print(result)