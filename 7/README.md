## Ollama integration

This project now uses `langchain_ollama` for both chat and embeddings while keeping existing class names (`ChatGLM`, `ChatGLMEmbeddings`).

Installation:

```bash
pip install langchain-ollama langchain-core
# Install/ensure ollama is running locally
# macOS: brew install ollama && ollama serve
```

Pull required models:

```bash
ollama pull gpt-oss:120b-cloud
ollama pull nomic-embed-text:latest
```

Environment (optional):

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export MODEL_ID=gpt-oss:120b-cloud
export EMBEDDING_MODEL=nomic-embed-text:latest
```

Notes:
- `ZHIPU_API_KEY` is no longer required.
- You can still pass `api_key` to `ChatGLM`/`ChatGLMEmbeddings`; it will be ignored for compatibility.
# lat  
## 介绍

LLM Auto Test Tool，这是一个利用RAG技术调用大模型完成测试接口测试的实验性项目。
![](assets/17154097369951.jpg)
这里用到了RAG、few-shot、CoT等大模型相关的技术，实现了从自然语言到测试执行的过程。
