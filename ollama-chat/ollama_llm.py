import ollama

from typing import Iterator


class OllamaLLM:
    """Ollama LLM 模块

    为方便使用，再次封装 ollama 库
    """

    def __init__(self, client: ollama.Client) -> None:
        self._client: ollama.Client = client
        self._model: str = ""
        self._num_ctx: int = 2048
        self._temperature: float = 0.7

    def set_model(self, model: str) -> None:
        """设置模型

        :param model: ollama 模型 id
        :type model: str
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 model 不在 Ollama 服务端已拉取的模型列表中
        """
        model_list: list[str | None] = [
            elem.model for elem in self._client.list().models
        ]

        if model not in model_list or not model.strip():
            raise ValueError(f"[ERROR] model={model} not found")

        self._model: str = model

    def set_num_ctx(self, num_ctx: int) -> None:
        """设置上下文窗口大小

        :param num_ctx: 上下文窗口大小
        :type num_ctx: int
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 num_ctx 小于 2048
        """
        if num_ctx < 2048:
            raise ValueError(f"[ERROR] The number of num_ctx={num_ctx} is too small")

        self._num_ctx: int = num_ctx

    def set_temperature(self, temperature: float) -> None:
        """设置温度

        温度范围 0.0 ~ 1.0

        :param temperature: 温度大小
        :type temperature: float
        :returns: 无
        :rtype: None
        :raises ValueError: 如果 temperature 不在 0.0 ~ 1.0 范围内
        """
        if temperature < 0.0 or temperature > 1.0:
            raise ValueError(
                f"[ERROR] The number of temperature={temperature} is not between 0.0 and 1.0"
            )

        self._temperature: float = temperature

    def get_num_ctx(self) -> int:
        """获取上下文窗口大小

        :return: 上下文窗口大小
        :rtype: int
        """
        return self._num_ctx

    def chat(
        self, messages: list[dict[str, str]], think: bool
    ) -> Iterator[tuple[str, str]]:
        """生成 AI 响应流

        AI 响应流 = (思考流, 内容流)

        如果一个流不为空，则另一个流必为空

        :param messages: 消息列表
        :type messages: list[dict[str, str]]
        :param think: 思考模式开关
        :type think: bool
        :return: (思考流, 内容流) 的迭代器
        :rtype: Iterator[tuple[str, str]]
        """
        for part in self._client.chat(
            model=self._model,
            options={"num_ctx": self._num_ctx, "temperature": self._temperature},
            messages=messages,
            stream=True,
            think=think,
        ):
            yield (
                part["message"].get("thinking", ""),
                part["message"].get("content", ""),
            )
