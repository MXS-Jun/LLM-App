import re
import math


def conservative_token_estimate(text: str) -> int:
    """保守估计字符串分词后所占的 token 数

    在无法提取模型的分词器的情况下，用该函数保守估计 token 数

    :param text: 待估计的字符串
    :type text: str
    :returns: 保守估计的 token 数
    :rtype: int
    """
    # 中文字符数
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", text))
    # 非中文字符数
    non_chinese_chars = len(
        re.findall(r"[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", text)
    )
    # 表情数
    emoji_count = len(re.findall(r"[\U00010000-\U0010ffff]", text))

    # 平均每个中文字符占 1.3 token
    chinese_tokens = int(math.ceil(chinese_chars * 1.3))
    # 平均每个非中文字符占 0.6 token
    non_chinese_tokens = (
        max(1, int(math.ceil(non_chinese_chars * 0.6))) if non_chinese_chars > 0 else 0
    )
    # 平均每个表情占 2 token
    emoji_tokens = emoji_count * 2

    total = chinese_tokens + non_chinese_tokens + emoji_tokens

    # 额外加 5% buffer 防边界情况
    return int(total * 1.05 + 1)


class Memory:
    """记忆模块

    针对 ollama 和 gradio.Chatbot 组件设计，管理系统提示词和对话历史
    """

    def __init__(self) -> None:
        # 系统消息
        self._system_message: dict = {
            "role": "system",
            "content": "",
        }
        # AI 回答不包括思考过程的消息列表
        self._messages: list[dict[str, str]] = []
        # AI 回答包括思考过程的消息列表
        self._history: list[dict[str, str]] = []

    def set_system_message(self, content: str) -> None:
        """设置系统消息

        :param  content: 系统提示词
        :type content: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 content 为 None 或空
        """
        if content is None or not content.strip():
            raise ValueError("[ERROR] The content of system messsage is empty")

        self._system_message["content"] = content

    def add_user_message(self, content: str) -> None:
        """添加用户消息

        :param content: 用户消息内容
        :type content: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 content 为 None 或空
        """
        if content is None or not content.strip():
            raise ValueError("[ERROR] The content of user message is empty")

        self._messages.append({"role": "user", "content": content})
        self._history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """添加 AI 消息

        :param content: AI 消息内容，不包括思考过程
        :type content: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 content 为 None 或空
        """
        if content is None or not content.strip():
            raise ValueError("[ERROR] The content of assistant message is empty")

        self._messages.append({"role": "assistant", "content": content})

    def add_assistant_response(self, content: str) -> None:
        """添加 AI 响应

        :param content: AI 响应内容，包括思考过程
        :type content: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 content 为 None 或空
        """
        if content is None or not content.strip():
            raise ValueError("[ERROR] The content of assistant response is empty")

        self._history.append({"role": "assistant", "content": content})

    def get_system_message(self) -> dict[str, str]:
        """获取系统消息

        :returns: 系统消息
        :rtype: dict[str, str]
        """
        return self._system_message.copy()

    def get_history(self) -> list[dict[str, str]]:
        """获取 gradio.Chatbot 组件需要的消息列表

        :returns: 包括思考过程的消息列表
        :rtype: list[dict[str, str]]
        """
        return self._history.copy()

    def get_context(self, num_ctx: int) -> list[dict[str, str]]:
        """根据上下文窗口大小，消息列表的倒数 n 条消息

        消息列表不包括思考过程，限制 n 为奇数（多轮对话 + 最新用户消息）

        :param num_ctx: 上下文窗口大小
        :type num_ctx: int
        :returns: 消息列表的倒数 n 条消息按顺序构成的列表
        :rtype: list[dict[str, str]]
        :raises ValueError: 如果 num_ctx 太小，以至于无法容纳系统提示词 + 最新用户消息
        """
        n: int = 0
        tokens: int = conservative_token_estimate(self._system_message["content"])

        # 系统提示词字符数不能大于上下文窗口大小
        if tokens > num_ctx:
            raise ValueError(f"[ERROR] The number of num_ctx={num_ctx} is too small")

        for message in reversed(self._messages):
            tokens += conservative_token_estimate(message["content"])
            if tokens >= num_ctx:
                break
            else:
                n += 1

        # 如果 n 为偶数，则减 1，不仅可以调整为奇数，而且可以留出上下文窗口以生成 AI 响应
        if n > 0 and n % 2 == 0:
            n -= 1

        # n 为 0 意味着剩下的上下文窗口无法容纳最新用户消息
        if n == 0:
            raise ValueError(f"[ERROR] The number of num_ctx={num_ctx} is too small")

        return self._messages[-n:]

    def clear(self) -> None:
        """清空消息列表

        不重置系统提示词

        :returns: 无
        :rtype: None
        """
        self._messages.clear()
        self._history.clear()

    def __len__(self) -> int:
        """返回消息列表的长度

        :return: 消息列表的长度，不包括系统消息
        :rtype: int
        """
        return len(self._messages)
