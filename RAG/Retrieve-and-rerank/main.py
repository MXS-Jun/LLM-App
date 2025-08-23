import gradio as gr
import textwrap
import yaml

from pathlib import Path
from typing import List
from embedder import Embedder
from generator import Generator
from vector_db import VectorDB
from retriever import Retriever


# 加载配置文件
CONFIG_YAML_PATH = Path(__file__).parent / "config.yaml"
CONFIG = yaml.safe_load(CONFIG_YAML_PATH.read_text())
# 实例化嵌入器
EMBEDDER = Embedder(config=CONFIG["embedder"])
# 实例化生成器
GENERATOR = Generator(config=CONFIG["generator"])
# 实例化向量数据库
VECTOR_DB = VectorDB(config=CONFIG["vector_db"])
VECTOR_DB.set_embedder(embedder=EMBEDDER)
# 实例化检索器
RETRIEVER = Retriever(config=CONFIG["retriever"])
RETRIEVER.set_embedder(embedder=EMBEDDER)
RETRIEVER.set_vector_db(vector_db=VECTOR_DB)


def get_retrieved_documents(user_content: str) -> str:
    global RETRIEVER

    context = RETRIEVER.query(text_list=[user_content])
    context = context[0]

    retrieved_documents = ""
    if context is not None:
        retrieved_documents = "\n\n---\n\n".join(
            [f"### 文档 {idx+1}\n\n{doc.strip()}" for idx, doc in enumerate(context)]
        )

    return retrieved_documents


def chatbot_response(user_content: str, chat_history: List):
    global GENERATOR

    retrieved_documents = get_retrieved_documents(user_content)
    user_question = user_content

    prompt_template = textwrap.dedent(
        """
        已知以下文档片段是与问题相关的参考信息：
        {retrieved_documents}

        请基于上述文档内容，回答以下问题：{user_question}

        回答要求：
        1. 严格以提供的文档片段为依据，优先使用文档中明确提及的信息、数据或观点；
        2. 若文档中未直接包含回答所需的信息，需明确说明“文档中未提及相关内容”，不擅自补充外部知识；
        3. 保持回答简洁、准确，逻辑清晰，避免冗余表述；
        4. 若文档中存在多个相关观点或信息，需全部涵盖并说明其关联性（如“文档提到 A，同时指出 B 与 A 相关”）。
        """
    )
    prompt = prompt_template.format(
        retrieved_documents=retrieved_documents, user_question=user_question
    )

    response = ""
    for content in GENERATOR.generate(prompt, chat_history):
        response += content
        yield response, None

    yield response, retrieved_documents


def update_collection() -> None:
    global VECTOR_DB

    if VECTOR_DB.update_collection():
        gr.Info(message="Update Knowledge Base successfully", duration=10)
    else:
        gr.Info(message="Failed to update Knowledge Base", duration=10)


if __name__ == "__main__":
    with gr.Blocks(title="Naive RAG") as demo:
        with gr.Tab("ChatBot"):
            with gr.Sidebar():
                ref_docs = gr.Markdown()

            chat_iface = gr.ChatInterface(
                fn=chatbot_response,
                type="messages",
                title="Naive RAG",
                description="Please enter your question, and I will do my best to answer it.",
                additional_outputs=[ref_docs],
            )
        with gr.Tab("Knowledge Base"):
            update_knowledge_base = gr.Button(value="Update Knowledge Base")
            update_knowledge_base.click(fn=update_collection, inputs=None, outputs=None)

    demo.launch()
