import copy
import gradio as gr
from typing import Generator, List, Dict, Any, Optional
from ollama_llm import OllamaLLM


class OllamaChatbot:
    def __init__(self):
        # 初始化默认配置
        self.default_chat_api_url = "http://localhost:11434/api/chat"
        self.default_model = "deepseek-r1:8b"
        self.default_system_prompt = "你是能干的AI助手，让我们一步一步思考。"
        self.default_temperature = 10 * 0.05
        self.default_num_ctx = 8 * 1024

        # 初始化LLM和聊天历史
        self.llm = OllamaLLM(
            model=self.default_model, chat_api_url=self.default_chat_api_url
        )
        self.llm.set_system_message(self.default_system_prompt)
        self.llm.set_temperature(self.default_temperature)
        self.llm.set_num_ctx(self.default_num_ctx)
        self.llm.set_think(False)
        self.chat_history: List[Dict[str, str]] = []

    def update_send_input_btn_state(self, text: str) -> Dict[str, Any]:
        """更新发送按钮状态"""
        is_valid = bool(text and text.strip())
        return gr.update(interactive=is_valid)

    def get_completion(
        self, user_content: str
    ) -> Generator[List[Dict[str, str]], None, None]:
        """获取AI回复并流式返回"""
        if not user_content or not user_content.strip():
            return

        # 添加用户消息到历史
        self.chat_history.append({"role": "user", "content": user_content})
        yield copy.deepcopy(self.chat_history)

        # 准备接收AI回复
        self.chat_history.append({"role": "assistant", "content": ""})
        self.llm.add_user_message(user_content)

        # 流式获取并更新回复
        try:
            for token in self.llm.get_response_stream():
                self.chat_history[-1]["content"] += token
                yield copy.deepcopy(self.chat_history)
        except Exception as e:
            self.chat_history[-1]["content"] += f"\n\n发生错误: {str(e)}"
            yield copy.deepcopy(self.chat_history)

    def set_think_mode(self, think: bool) -> None:
        """设置思考模式"""
        self.llm.set_think(think)

    def clear_chat_record(self) -> List[Dict[str, str]]:
        """清空聊天记录"""
        # 保留系统消息
        self.llm.messages = self.llm.messages[0:1] if self.llm.messages else []
        self.chat_history = []
        return []

    def restore_settings(self) -> List[Any]:
        """恢复默认设置"""
        return [
            self.default_chat_api_url,
            self.default_model,
            self.default_system_prompt,
            self.default_temperature,
            self.default_num_ctx,
        ]

    def update_settings(
        self,
        chat_api_url: str,
        model: str,
        system_prompt: str,
        temperature: float,
        num_ctx: int,
    ) -> None:
        """更新模型设置"""
        try:
            self.llm.set_chat_api_url(chat_api_url)
            self.llm.set_model(model)
            self.llm.set_system_message(system_prompt)
            self.llm.set_temperature(temperature)
            self.llm.set_num_ctx(num_ctx)
        except Exception as e:
            print(f"更新设置失败: {str(e)}")

    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面"""
        with gr.Blocks() as demo:
            with gr.Tab(label="聊天"):
                chatbot_info_md = gr.Markdown(value="# 🤖 聊天机器人\n你的智能AI助手")
                chat_history_chatbot = gr.Chatbot(
                    show_label=False, type="messages", resizable=True
                )
                input_textbox = gr.Textbox(label="输入框", lines=8)

                with gr.Row():
                    think_mode_checkbox = gr.Checkbox(label="思考模式")
                    send_input_btn = gr.Button(value="发送", interactive=False)

                clear_chat_record_btn = gr.Button(value="清空聊天记录")

            with gr.Tab(label="设置"):
                settings_info_md = gr.Markdown(
                    value="# 本地Ollama引擎\n可以调用在本地部署的Ollama大模型引擎"
                )
                chat_api_url_textbox = gr.Textbox(
                    label="自定义API接口地址",
                    value=self.default_chat_api_url,
                    interactive=True,
                )
                model_name_textbox = gr.Textbox(
                    label="自定义模型名", value=self.default_model, interactive=True
                )
                system_prompt_textbox = gr.Textbox(
                    label="自定义系统提示词",
                    lines=8,
                    value=self.default_system_prompt,
                    interactive=True,
                )
                temperature_slider = gr.Slider(
                    label="温度",
                    minimum=0 * 0.05,
                    maximum=40 * 0.05,
                    step=0.05,
                    value=self.default_temperature,
                    interactive=True,
                )
                num_ctx_slider = gr.Slider(
                    label="上下文窗口大小",
                    minimum=2 * 1024,
                    maximum=32 * 1024,
                    step=1024,
                    value=self.default_num_ctx,
                    interactive=True,
                )

                with gr.Row():
                    restore_btn = gr.Button(value="恢复默认")
                    save_btn = gr.Button(value="保存设置")

            # 设置事件监听
            input_textbox.change(
                fn=self.update_send_input_btn_state,
                inputs=[input_textbox],
                outputs=[send_input_btn],
            )

            send_input_btn.click(
                fn=self.get_completion,
                inputs=[input_textbox],
                outputs=[chat_history_chatbot],
            ).then(
                fn=lambda: gr.update(value=""),  # 发送后清空输入框
                inputs=None,
                outputs=[input_textbox],
            )

            think_mode_checkbox.change(
                fn=self.set_think_mode, inputs=[think_mode_checkbox], outputs=None
            )

            clear_chat_record_btn.click(
                fn=self.clear_chat_record, inputs=None, outputs=chat_history_chatbot
            )

            restore_btn.click(
                fn=self.restore_settings,
                inputs=None,
                outputs=[
                    chat_api_url_textbox,
                    model_name_textbox,
                    system_prompt_textbox,
                    temperature_slider,
                    num_ctx_slider,
                ],
            )

            save_btn.click(
                fn=self.update_settings,
                inputs=[
                    chat_api_url_textbox,
                    model_name_textbox,
                    system_prompt_textbox,
                    temperature_slider,
                    num_ctx_slider,
                ],
                outputs=None,
            )

        return demo


if __name__ == "__main__":
    chatbot = OllamaChatbot()
    demo = chatbot.create_interface()
    demo.launch()
