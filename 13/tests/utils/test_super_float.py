import pytest
from queryrewrite.utils.super_float import SuperFloat, extract_float


class TestSuperFloat:
    """Test cases for SuperFloat class."""
    
    def test_extract_single_number(self):
        """Test extracting a single number from string."""
        result = SuperFloat("The price is 123.45 dollars")
        assert result == 123.45
        assert isinstance(result, SuperFloat)
    
    def test_extract_first_number_from_multiple(self):
        """Test extracting the first number when multiple numbers exist."""
        result = SuperFloat("Price: 123.45, Quantity: 67.89, Total: 99.99")
        assert result == 123.45
        assert isinstance(result, SuperFloat)
    
    def test_extract_negative_number(self):
        """Test extracting negative numbers."""
        result = SuperFloat("Temperature is -15.7 degrees")
        assert result == -15.7
    
    def test_extract_integer(self):
        """Test extracting integer values."""
        result = SuperFloat("Count: 42 items")
        assert result == 42.0
    
    def test_extract_scientific_notation(self):
        """Test extracting scientific notation."""
        result = SuperFloat("Value: 1.23e-4 meters")
        assert result == 1.23e-4
    
    def test_extract_number_with_commas(self):
        """Test extracting numbers with comma separators."""
        result = SuperFloat("Population: 1,234,567 people")
        assert result == 1234567.0
    
    def test_direct_numeric_input(self):
        """Test creating SuperFloat from numeric values."""
        result = SuperFloat(123.45)
        assert result == 123.45
        assert isinstance(result, SuperFloat)
    
    def test_from_string_classmethod(self):
        """Test the from_string class method."""
        result = SuperFloat.from_string("Score: 95.5 points")
        assert result == 95.5
        assert isinstance(result, SuperFloat)
    
    def test_extract_float_function(self):
        """Test the convenience extract_float function."""
        result = extract_float("Price: $99.99")
        assert result == 99.99
        assert isinstance(result, float)
    
    def test_no_number_in_string(self):
        """Test behavior when no number is found in string."""
        with pytest.raises(ValueError, match="No valid float found"):
            SuperFloat("No numbers here")
    
    def test_empty_string(self):
        """Test behavior with empty string."""
        with pytest.raises(ValueError, match="No valid float found"):
            SuperFloat("")
    
    def test_none_input(self):
        """Test behavior with None input."""
        with pytest.raises(TypeError):
            SuperFloat(None)
    
    def test_float_operations(self):
        """Test that SuperFloat behaves like a regular float in operations."""
        sf1 = SuperFloat("Value: 10.5")
        sf2 = SuperFloat("Value: 5.5")
        
        # Addition
        result = sf1 + sf2
        assert result == 16.0
        assert isinstance(result, float)
        
        # Multiplication
        result = sf1 * 2
        assert result == 21.0
        
        # Division
        result = sf1 / 2
        assert result == 5.25
    
    def test_string_representation(self):
        """Test string representation of SuperFloat."""
        sf = SuperFloat("Price: 123.45")
        assert str(sf) == "123.45"
        assert repr(sf) == "SuperFloat(123.45)"
    
    def test_complex_text_with_numbers(self):
        """Test extracting from complex text with various number formats."""
        text = "The experiment yielded 42.5% success rate, with 1,234 participants and 2.5e-3 error margin."
        result = SuperFloat(text)
        assert result == 42.5
    
    def test_numbers_with_currency_symbols(self):
        """Test extracting numbers with currency symbols."""
        result = SuperFloat("Price: $123.45")
        assert result == 123.45
        
        result = SuperFloat("Cost: €99.99")
        assert result == 99.99
    
    def test_numbers_with_percentages(self):
        """Test extracting numbers with percentage signs."""
        result = SuperFloat("Success rate: 85.5%")
        assert result == 85.5 