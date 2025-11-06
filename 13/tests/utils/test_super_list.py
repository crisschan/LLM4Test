import pytest
from queryrewrite.utils.super_list import SuperList, extract_list


class TestSuperList:
    """Test cases for SuperList class."""
    
    def test_extract_simple_list(self):
        """Test extracting a simple list from string."""
        result = SuperList('The items are: ["apple", "banana", "cherry"]')
        assert result == ["apple", "banana", "cherry"]
        assert isinstance(result, SuperList)
    
    def test_extract_first_list_from_multiple(self):
        """Test extracting the first list when multiple lists exist."""
        text = 'First: ["a", "b"], Second: ["x", "y"], Third: ["1", "2"]'
        result = SuperList(text)
        assert result == ["a", "b"]
        assert isinstance(result, SuperList)
    
    def test_extract_json_array(self):
        """Test extracting JSON array."""
        result = SuperList('Data: [1, 2, 3, 4, 5]')
        assert result == [1, 2, 3, 4, 5]
    
    def test_extract_nested_list(self):
        """Test extracting nested list."""
        result = SuperList('Matrix: [[1, 2], [3, 4], [5, 6]]')
        assert result == [[1, 2], [3, 4], [5, 6]]
    
    def test_extract_list_with_objects(self):
        """Test extracting list with dictionary objects."""
        text = 'Users: [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'
        result = SuperList(text)
        assert result == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    
    def test_extract_list_from_code_block(self):
        """Test extracting list from code block."""
        text = '''Here is the code:
```python
["item1", "item2", "item3"]
```
And some text.'''
        result = SuperList(text)
        assert result == ["item1", "item2", "item3"]
    
    def test_extract_list_from_json_block(self):
        """Test extracting list from JSON code block."""
        text = '''Here is the data:
```json
[1, 2, 3, 4, 5]
```
And some text.'''
        result = SuperList(text)
        assert result == [1, 2, 3, 4, 5]
    
    def test_direct_list_input(self):
        """Test creating SuperList from list values."""
        result = SuperList([1, 2, 3, 4, 5])
        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, SuperList)
    
    def test_direct_tuple_input(self):
        """Test creating SuperList from tuple values."""
        result = SuperList((1, 2, 3, 4, 5))
        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, SuperList)
    
    def test_from_string_classmethod(self):
        """Test the from_string class method."""
        result = SuperList.from_string('Items: ["red", "green", "blue"]')
        assert result == ["red", "green", "blue"]
        assert isinstance(result, SuperList)
    
    def test_extract_list_function(self):
        """Test the convenience extract_list function."""
        result = extract_list('Data: [10, 20, 30, 40]')
        assert result == [10, 20, 30, 40]
        assert isinstance(result, list)
    
    def test_no_list_in_string(self):
        """Test behavior when no list is found in string."""
        with pytest.raises(ValueError, match="No valid list found"):
            SuperList("No lists here")
    
    def test_empty_string(self):
        """Test behavior with empty string."""
        with pytest.raises(ValueError, match="No valid list found"):
            SuperList("")
    
    def test_none_input(self):
        """Test behavior with None input."""
        with pytest.raises(TypeError):
            SuperList(None)
    
    def test_list_operations(self):
        """Test that SuperList behaves like a regular list in operations."""
        sl1 = SuperList('Data: [1, 2, 3]')
        sl2 = SuperList('Data: [4, 5, 6]')
        
        # Addition
        result = sl1 + sl2
        assert result == [1, 2, 3, 4, 5, 6]
        assert isinstance(result, list)
        
        # Multiplication
        result = sl1 * 2
        assert result == [1, 2, 3, 1, 2, 3]
        
        # Length
        assert len(sl1) == 3
        
        # Indexing
        assert sl1[0] == 1
        assert sl1[-1] == 3
    
    def test_string_representation(self):
        """Test string representation of SuperList."""
        sl = SuperList('Data: ["a", "b", "c"]')
        assert str(sl) == "['a', 'b', 'c']"
        assert repr(sl) == "SuperList(['a', 'b', 'c'])"
    
    def test_complex_text_with_lists(self):
        """Test extracting from complex text with various list formats."""
        text = "The results show: [1, 2, 3], but also [4, 5, 6] and finally [7, 8, 9]"
        result = SuperList(text)
        assert result == [1, 2, 3]
    
    def test_list_with_mixed_types(self):
        """Test extracting list with mixed data types."""
        text = 'Mixed data: [1, "string", True, 3.14, {"key": "value"}]'
        result = SuperList(text)
        assert result == [1, "string", True, 3.14, {"key": "value"}]
    
    def test_empty_list(self):
        """Test extracting empty list."""
        result = SuperList('Empty: []')
        assert result == []
    
    def test_list_with_quotes(self):
        """Test extracting list with quoted strings."""
        result = SuperList('Names: ["John", "Jane", "Bob"]')
        assert result == ["John", "Jane", "Bob"]
    
    def test_list_with_single_quotes(self):
        """Test extracting list with single quoted strings."""
        result = SuperList("Names: ['John', 'Jane', 'Bob']")
        assert result == ["John", "Jane", "Bob"]