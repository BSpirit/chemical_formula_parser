"""Test cases for chemical_formula module."""
import unittest
import chemical_formula


class TokenizerTest(unittest.TestCase):
    """Test case for chemical.tokenize function."""

    def test_valid_tokens(self):
        """Checks valid token strings produces valid Token instances"""
        # given
        tokens = ['(', '{', '[', '1', '999', 'H', 'He', ')', '}', ']', '']

        # when
        for token in tokens:
            self.assertEqual(chemical_formula.tokenize(token).value, token)

    def test_invalid_token(self):
        """Checks chemical_formula.TokenizerException is raised when invalid token is
        provided.
        """
        # Given
        token = "+"

        # Then
        with self.assertRaises(chemical_formula.TokenizerException):
            chemical_formula.tokenize(token)


class LexerTestCase(unittest.TestCase):
    """Test case for chemical_formula.Lexer class."""

    def test_flat_formula(self):
        """Checks if a flat formula is properly tokenized."""
        # Given
        formula = "HHe2O30"
        lexer = chemical_formula.Lexer(formula)

        # Then
        expected = ['H', 'He', '2', 'O', '30']
        while lexer.peek().token_type is not chemical_formula.TokenType.EOF:
            position = lexer.position
            self.assertEqual(lexer.get_next_token().value, expected[position])

    def test_complex_formula(self):
        """Checks if a complex formula is properly tokenized."""
        # Given
        formula = "Mg2[CH4{NNi2(Li2O4)5}14]3"
        lexer = chemical_formula.Lexer(formula)

        # Then
        expected = ['Mg', '2', '[', 'C', 'H', '4', '{', 'N', 'Ni', '2', '(', 'Li', '2',
                    'O', '4', ')', '5', '}', '14', ']', '3']
        while lexer.peek().token_type is not chemical_formula.TokenType.EOF:
            position = lexer.position
            self.assertEqual(lexer.get_next_token().value, expected[position])


class ParserTestCase(unittest.TestCase):
    """Test case for chemical_formula.Parser class."""

    def test_empty_string(self):
        """Checks if empty string input raises chemical_formula.ParsingException"""
        # Given
        formula = ""
        lexer = chemical_formula.Lexer(formula)
        parser = chemical_formula.Parser(lexer)

        # Then
        with self.assertRaises(chemical_formula.ParsingException):
            parser.parse_formula()

    def test_flat_formula(self):
        """Checks if a simple formula is properly parsed."""
        # Given
        formula = "HHe2O30"
        lexer = chemical_formula.Lexer(formula)
        parser = chemical_formula.Parser(lexer)

        # When
        counter = parser.parse_formula()

        # Then
        expected = {'H': 1, 'He': 2, 'O': 30}
        self.assertDictEqual(counter, expected)

    def test_complex_formula(self):
        """Checks if a complex formula is properly parsed."""
        # Given
        formula = "Mg2[CH4{NNi2(Li2O4)5}14]3"
        lexer = chemical_formula.Lexer(formula)
        parser = chemical_formula.Parser(lexer)

        # When
        counter = parser.parse_formula()

        # Then
        expected = {'Mg': 2, 'C': 3, 'H': 12, 'N': 42, 'Ni': 84, 'Li': 420, 'O': 840}
        self.assertDictEqual(counter, expected)

    def test_unclosed_bracket(self):
        """Checks is unclosed brackets raises chemical_formula.ParsingException"""
        # Given
        formula = "H2(OH"
        lexer = chemical_formula.Lexer(formula)
        parser = chemical_formula.Parser(lexer)

        # Then
        with self.assertRaises(chemical_formula.ParsingException):
            parser.parse_formula()

    def test_unmatching_brackets(self):
        """Checks is unmatching brackets raises chemical_formula.ParsingException"""
        # Given
        formula = "H2(OH))2"
        lexer = chemical_formula.Lexer(formula)
        parser = chemical_formula.Parser(lexer)

        # Then
        with self.assertRaises(chemical_formula.ParsingException):
            parser.parse_formula()
