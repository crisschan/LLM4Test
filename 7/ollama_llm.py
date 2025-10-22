#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   ollama_llm.py
@Time    :   2025/10/15
@Author  :   CrissChan (refactor by assistant)
@Desc    :   LlamaIndex-compatible wrappers for Ollama chat and embeddings.
'''

from typing import Optional, List, Mapping, Any, Sequence, Dict
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.constants import DEFAULT_CONTEXT_WINDOW, DEFAULT_NUM_OUTPUTS
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
    ChatMessage,
    ChatResponse,
)
from llama_index.core.llms.callbacks import llm_completion_callback, llm_chat_callback
try:
    from llama_index.core.llms.types import MessageRole
except Exception:
    from enum import Enum
    class MessageRole(Enum):
        SYSTEM = "system"
        USER = "user"
        ASSISTANT = "assistant"
from typing import Any, List
from llama_index.core.embeddings import BaseEmbedding

# LangChain Ollama interfaces
from langchain_ollama import ChatOllama, OllamaEmbeddings as LCOllamaEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

DEFAULT_MODEL = 'gpt-oss:120b-cloud'

def to_message_dicts(messages: Sequence[ChatMessage])->List:
    return [
        {"role": message.role.value, "content": message.content,} 
                for message in messages if all([value is not None for value in message.values()])
    ]

def get_additional_kwargs() -> Dict:
    return {}

class OllamaLLM(CustomLLM):
    num_output: int = DEFAULT_NUM_OUTPUTS
    context_window: int = Field(default=DEFAULT_CONTEXT_WINDOW, description="The maximum number of context tokens for the model.", gt=0,)
    model: str = Field(default=DEFAULT_MODEL, description="The Ollama model to use, e.g., gpt-oss:120b-cloud")
    base_url: Optional[str] = Field(default=None, description="Optional Ollama base URL, e.g., http://localhost:11434")
    api_key: Optional[str] = Field(default=None, description="Ignored. Present for backward compatibility.")
    reuse_client: bool = Field(default=True, description=(
            "Reuse the client between requests. When doing anything with large "
            "volumes of async API calls, setting this to false can improve stability."
        ),
    )

    _client: Optional[Any] = PrivateAttr()
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        reuse_client: bool = True,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            reuse_client=reuse_client,
            api_key=api_key,
            **kwargs,
        )
        self.base_url = base_url
        self._client = None

    def _get_client(self) -> ChatOllama:
        if not self.reuse_client:
            return ChatOllama(model=self.model, base_url=self.base_url) if self.base_url else ChatOllama(model=self.model)

        if self._client is None:
            self._client = ChatOllama(model=self.model, base_url=self.base_url) if self.base_url else ChatOllama(model=self.model)
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "ollama_llm"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model,
        )

    def _chat(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        lc_messages: List[Any] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        client = self._get_client()
        if stream:
            return client.stream(lc_messages)
        return client.invoke(lc_messages)

    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        message_dicts: List = to_message_dicts(messages)
        response = self._chat(message_dicts, stream=False)
        content = response.content if hasattr(response, "content") else str(response)
        rsp = ChatResponse(
            message=ChatMessage(content=content, role=MessageRole.ASSISTANT, additional_kwargs={}),
            raw=response,
            additional_kwargs=get_additional_kwargs(),
        )
        return rsp

    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> CompletionResponseGen:
        response_txt = ""
        message_dicts: List = to_message_dicts(messages)
        stream = self._chat(message_dicts, stream=True)
        for chunk in stream:
            token = getattr(chunk, "content", None)
            if token is None:
                token = str(chunk)
            response_txt += token
            yield ChatResponse(
                message=ChatMessage(content=response_txt, role=MessageRole.ASSISTANT, additional_kwargs={}),
                delta=token,
                raw=chunk,
            )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        messages = [{"role": "user", "content": prompt}]
        response = self._chat(messages, stream=False)
        text = response.content if hasattr(response, "content") else str(response)
        rsp = CompletionResponse(text=text, raw=response, additional_kwargs=get_additional_kwargs())
        return rsp

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        response_txt = ""
        messages = [{"role": "user", "content": prompt}]
        stream = self._chat(messages, stream=True)
        for chunk in stream:
            token = getattr(chunk, "content", None)
            if token is None:
                token = str(chunk)
            response_txt += token
            yield CompletionResponse(text=response_txt, delta=token)


class OllamaEmbeddings(BaseEmbedding):
    model: str = Field(default='nomic-embed-text:latest', description="The Ollama embedding model to use.")
    base_url: Optional[str] = Field(default=None, description="Optional Ollama base URL, e.g., http://localhost:11434")
    reuse_client: bool = Field(default=True, description=(
            "Reuse the client between requests. When doing anything with large "
            "volumes of async API calls, setting this to false can improve stability."
        ),
    )

    _client: Optional[Any] = PrivateAttr()
    def __init__(
        self,
        model: str = 'nomic-embed-text:latest',
        reuse_client: bool = True,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model,
            reuse_client=reuse_client,
            **kwargs,
        )
        self.base_url = base_url
        self._client = None

    def _get_client(self) -> LCOllamaEmbeddings:
        if not self.reuse_client:
            return LCOllamaEmbeddings(model=self.model, base_url=self.base_url) if self.base_url else LCOllamaEmbeddings(model=self.model)

        if self._client is None:
            self._client = LCOllamaEmbeddings(model=self.model, base_url=self.base_url) if self.base_url else LCOllamaEmbeddings(model=self.model)
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "ollama_embedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        return self.get_general_text_embedding(query)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self.get_general_text_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        return self.get_general_text_embedding(text)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self.get_general_text_embedding(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings_list: List[List[float]] = []
        for text in texts:
            embeddings = self.get_general_text_embedding(text)
            embeddings_list.append(embeddings)
        return embeddings_list

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._get_text_embeddings(texts)

    def get_general_text_embedding(self, prompt: str) -> List[float]:
        client = self._get_client()
        return client.embed_query(prompt)


