import re
from typing import Union, Optional


class SuperFloat(float):
    """
    A float subclass that can extract numeric values from strings.
    
    This class extends the built-in float type and provides functionality
    to extract the first float number from a string containing multiple numbers
    separated by text.
    """
    
    def __new__(cls, value: Union[str, float, int]) -> 'SuperFloat':
        """
        Create a new SuperFloat instance.
        
        Args:
            value: String containing numbers or a numeric value
            
        Returns:
            SuperFloat instance with the extracted or converted value
        """
        if isinstance(value, str):
            # Extract the first float from the string
            extracted_value = cls._extract_first_float(value)
            if extracted_value is not None:
                return super().__new__(cls, extracted_value)
            else:
                raise ValueError(f"No valid float found in string: {value}")
        else:
            # If it's already a number, convert it normally
            return super().__new__(cls, value)
    
    @staticmethod
    def _extract_first_float(text: str) -> Optional[float]:
        """
        Extract the first float number from a string.
        
        Args:
            text: String that may contain numbers
            
        Returns:
            First float found in the string, or None if no valid float found
        """
        if not isinstance(text, str):
            return None
        
        # Pattern to match float numbers (including scientific notation)
        # This pattern matches:
        # - Integers: 123, -456
        # - Decimals: 123.456, -789.012
        # - Scientific notation: 1.23e-4, -5.67E+8
        # - Numbers with commas: 1,234.56
        float_pattern = r'-?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][+-]?\d+)?'
        
        # Find all matches
        matches = re.findall(float_pattern, text)
        
        if matches:
            # Convert the first match to float
            # Remove commas from the string before converting
            first_match = matches[0].replace(',', '')
            try:
                return float(first_match)
            except ValueError:
                return None
        
        return None
    
    @classmethod
    def from_string(cls, text: str) -> 'SuperFloat':
        """
        Create a SuperFloat from a string containing numbers.
        
        Args:
            text: String that may contain numbers
            
        Returns:
            SuperFloat instance
            
        Raises:
            ValueError: If no valid float is found in the string
        """
        return cls(text)
    
    def __repr__(self) -> str:
        """Return string representation of the SuperFloat."""
        return f"SuperFloat({super().__repr__()})"
    
    def __str__(self) -> str:
        """Return string representation of the SuperFloat."""
        return str(float(self))


# Convenience function for easy usage
def extract_float(text: str) -> float:
    """
    Extract the first float from a string.
    
    Args:
        text: String that may contain numbers
        
    Returns:
        First float found in the string
        
    Raises:
        ValueError: If no valid float is found in the string
    """
    return SuperFloat(text)
