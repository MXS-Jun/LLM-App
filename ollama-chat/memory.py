class Memory:
    """记忆模块

    用于管理对话历史，针对 ollama 和 gradio.Chatbot 组件设计
    """

    def __init__(self) -> None:
        # Ollama 消息格式的系统提示词，用于生成 AI 响应
        self._system_prompt: dict = {
            "role": "system",
            "content": "",
        }

        # Ollama 消息格式的消息列表，用于生成 AI 响应，不包括思考过程
        self._messages: list[dict[str, str]] = []

        # gradio.Chatbot 组件需要的对话历史列表，用于前端渲染，包括思考过程
        self._history: list[dict[str, str]] = []

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词

        :param  prompt: 系统提示词
        :type prompt: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 prompt 为 None 或空白字符串
        """
        if prompt is None or not prompt.strip():
            raise ValueError("[ERROR] system prompt is empty")

        self._system_prompt["content"] = prompt

    def add_user_message(self, message: str) -> None:
        """添加用户消息

        :param message: 用户消息
        :type message: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 message 为 None 或空白字符串
        """
        if message is None or not message.strip():
            raise ValueError("[ERROR] user message is empty")

        self._messages.append({"role": "user", "content": message})
        self._history.append({"role": "user", "content": message})

    def add_ai_message(self, message: str) -> None:
        """添加 AI 消息

        :param message: AI 消息，不包括思考过程
        :type message: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 message 为 None 或空白字符串
        """
        if message is None or not message.strip():
            raise ValueError("[ERROR] ai message is empty")

        self._messages.append({"role": "assistant", "content": message})

    def add_ai_response(self, response: str) -> None:
        """添加 AI 响应

        :param message: AI 响应，包括思考过程
        :type message: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 response 为 None 或空白字符串
        """
        if response is None or not response.strip():
            raise ValueError("[ERROR] ai response is empty")

        self._history.append({"role": "assistant", "content": response})

    def get_system_prompt(self) -> dict[str, str]:
        """获取系统提示词

        :returns: Ollama 消息格式的系统提示词
        :rtype: dict[str, str]
        """
        return self._system_prompt.copy()

    def get_history(self) -> list[dict[str, str]]:
        """获取 gradio.Chatbot 组件需要的对话历史列表

        完整的对话历史，用于前端渲染，包括思考过程

        :returns: 适配 gradio.Chatbot 组件输入要求的对话历史列表，包括思考过程
        :rtype: list[dict[str, str]]
        """
        return self._history.copy()

    def get_context(self, num_ctx: int) -> list[dict[str, str]]:
        """获取 Ollama 消息格式的消息列表

        系统提示词加上倒数 n 条消息，不包括思考过程，用于生成 AI 响应，
        系统提示词和倒数 n 条消息的字符总数不大于 num_ctx

        :param num_ctx: 上下文窗口大小
        :type num_ctx: int
        :returns: 系统提示词加上倒数 n 条消息
        :rtype: list[dict[str, str]]
        :raises ValueError: 如果 num_ctx 太小，以至于无法容纳系统提示词或无法容纳一条用户消息
        """
        n: int = 0
        count: int = len(self._system_prompt["content"])

        if count > num_ctx:
            raise ValueError(f"[ERROR] num_ctx={num_ctx} is too small")

        for message in reversed(self._messages):
            count += len(message["content"])
            if count >= num_ctx:
                break
            else:
                n += 1

        if n > 0 and n % 2 == 0:
            n -= 1

        if n == 0:
            raise ValueError(f"[ERROR] num_ctx={num_ctx} is too small")

        return self._messages[-n:]

    def clear(self) -> None:
        """清空消息列表和对话历史列表

        不重置系统提示词

        :returns: 无
        :rtype: None
        """
        self._messages.clear()
        self._history.clear()

    def __len__(self) -> int:
        """返回消息列表（对话历史列表）的长度

        消息列表的长度等于对话历史列表的长度，
        计算长度时，不包括系统提示词

        :return: 等于 AI 消息加上用户消息的数量
        :rtype: int
        """
        return len(self._messages)