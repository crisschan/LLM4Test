import re
import json
from typing import Union, Optional, List, Any


class SuperList(list):
    """
    A list subclass that can extract list data from LLM responses.
    
    This class extends the built-in list type and provides functionality
    to extract the first complete list from a string containing multiple lists
    or list-like structures.
    """
    
    def __init__(self, value: Union[str, list, tuple]):
        """
        Initialize SuperList with a value.
        
        Args:
            value: String containing lists or a list/tuple value
        """
        if isinstance(value, str):
            # Extract the first list from the string
            extracted_value = self._extract_first_list(value)
            if extracted_value is not None:
                super().__init__(extracted_value)
            else:
                raise ValueError(f"No valid list found in string: {value}")
        else:
            # If it's already a list or tuple, convert it normally
            super().__init__(value)
    
    @staticmethod
    def _extract_first_list(text: str) -> Optional[List[Any]]:
        """
        Extract the first complete list from a string.
        
        Args:
            text: String that may contain lists
            
        Returns:
            First list found in the string, or None if no valid list found
        """
        if not isinstance(text, str):
            return None
        
        # Strategy 1: Try to parse the entire text as JSON (if it's a pure JSON array)
        try:
            parsed = json.loads(text.strip())
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Strategy 2: Look for JSON arrays in code blocks (most common in LLM responses)
        code_block_patterns = [
            r'```(?:python|json)?\s*(\[.*?\])\s*```',
            r'`(\[.*?\])`',
        ]
        
        for pattern in code_block_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    parsed_list = json.loads(match.group(1))
                    if isinstance(parsed_list, list):
                        return parsed_list
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Strategy 3: Convert single quotes to double quotes for JSON parsing
        # Find patterns like ['item1', 'item2'] and convert to ["item1", "item2"]
        single_quote_pattern = r'\[\s*\'[^\']*\'(?:\s*,\s*\'[^\']*\')*\s*\]'
        match = re.search(single_quote_pattern, text, re.DOTALL)
        if match:
            try:
                # Replace single quotes with double quotes for JSON parsing
                json_str = match.group(0).replace("'", '"')
                parsed_list = json.loads(json_str)
                if isinstance(parsed_list, list):
                    return parsed_list
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Strategy 4: Look for nested lists specifically
        nested_list_pattern = r'\[\s*\[.*?\](?:\s*,\s*\[.*?\])*\s*\]'
        match = re.search(nested_list_pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(0)
                # 确保嵌套列表中的所有元素都是有效的JSON
                parsed_list = json.loads(json_str)
                if isinstance(parsed_list, list) and all(isinstance(item, list) for item in parsed_list):
                    return parsed_list
            except (json.JSONDecodeError, ValueError):
                pass
                
        # Strategy 5: Look for JSON arrays using more specific patterns
        # This pattern looks for complete JSON arrays with proper structure
        json_patterns = [
            r'\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\]',  # Array of strings
            r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]',  # Array of numbers
            r'\[\s*{[^}]*}(?:\s*,\s*{[^}]*})*\s*\]',  # Array of objects
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    parsed_list = json.loads(match.group(0))
                    if isinstance(parsed_list, list):
                        return parsed_list
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Strategy 6: Handle mixed type arrays
        mixed_type_pattern = r'\[\s*(?:[^\[\]]*|\[[^\[\]]*\])*\]'
        match = re.search(mixed_type_pattern, text, re.DOTALL)
        if match:
            try:
                # Try to fix common issues with mixed type arrays
                json_str = match.group(0)
                # Replace single quotes with double quotes
                json_str = json_str.replace("'", '"')
                # Handle boolean values (True/False -> true/false)
                json_str = json_str.replace('True', 'true').replace('False', 'false')
                parsed_list = json.loads(json_str)
                if isinstance(parsed_list, list):
                    return parsed_list
            except (json.JSONDecodeError, ValueError):
                pass
        
        return None
    
    @classmethod
    def from_string(cls, text: str) -> 'SuperList':
        """
        Create a SuperList from a string containing lists.
        
        Args:
            text: String that may contain lists
            
        Returns:
            SuperList instance
            
        Raises:
            ValueError: If no valid list is found in the string
        """
        return cls(text)
    
    def __repr__(self) -> str:
        """Return string representation of the SuperList."""
        return f"SuperList({super().__repr__()})"
    
    def __str__(self) -> str:
        """Return string representation of the SuperList."""
        return str(list(self))


# Convenience function for easy usage
def extract_list(text: str) -> List[Any]:
    """
    Extract the first list from a string.
    
    Args:
        text: String that may contain lists
        
    Returns:
        First list found in the string
        
    Raises:
        ValueError: If no valid list is found in the string
    """
    return SuperList(text)
