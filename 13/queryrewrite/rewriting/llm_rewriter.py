import json
from typing import List
import os

from queryrewrite.llm.base import LLMBase
from queryrewrite.utils.data_models import Query, RewrittenQuery
from queryrewrite.utils.super_json import SuperJSON

class LLMRewriter:
    """Rewrites a query using a large language model."""

    def __init__(self, llm: LLMBase, thinking: str = ''):
        self.llm = llm
        self.thinking = thinking
        self.response_parser = SuperJSON()
        
        # Load system prompt from external file
        prompt_path = os.path.join(os.path.dirname(__file__), "llm_rewriter_prompt.txt")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            print(f"Error: Prompt file not found at {prompt_path}")
            self.system_prompt = "" # Fallback to empty prompt

    def rewrite(self, query: Query) -> List[RewrittenQuery]:
        """ 
        Rewrites the query using the LLM.

        Args:
            query: The query to rewrite.

        Returns:
            A list of rewritten queries.
        """
        # Safely serialize the input data to prevent prompt injection
        user_input_json = json.dumps({"query": query["query"], "reference": query["reference"]}, ensure_ascii=False)
        
        prompt = f'{self.thinking}\n\n{self.system_prompt}\n\n{user_input_json}'
        
        response = self.llm.invoke(prompt)
        
        try:
            parsed_response = self.response_parser.loads(response)
            
            if isinstance(parsed_response, list) and all("query" in item and "reference" in item for item in parsed_response):
                return parsed_response
            
            elif isinstance(parsed_response, dict) and "response" in parsed_response:
                resp_content = parsed_response["response"]
                if isinstance(resp_content, list):
                    # Check sub-list format
                    if all("query" in item and "reference" in item for item in resp_content):
                         return resp_content
                # Fallback for single raw string in "response"
                return [{"query": str(resp_content).strip(), "reference": query["reference"]}]
            
            else:
                # If format is completely unexpected, fallback to raw response
                raise ValueError(f"Unexpected parsed format: {type(parsed_response)}")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Parse failed ({type(e).__name__}): {e}. Falling back to raw response.")
            return [{"query": response.strip(), "reference": query["reference"]}]
