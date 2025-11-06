from typing import List, Dict, Any

# Using TypedDict for structured dictionaries
from typing import TypedDict

class Query(TypedDict):
    query: str
    reference: str

class RewrittenQuery(TypedDict):
    query: str
    reference: str

Glossary = List[List[str]]
