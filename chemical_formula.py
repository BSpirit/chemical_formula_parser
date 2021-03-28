"""This module can be used to parse a chemical formula.

The related grammar is the following:
formula :=  molecule EOF
molecule := group molecule?
group := ATOM FACTOR? | OPENING_BRACKET molecule CLOSING_BRACKET FACTOR?

ATOM: '[A-Z][a-z]?'
FACTOR: '\\d+'
OPENING_BRACKET: '[\\[({]'
CLOSING_BRACKET: '[})\\]]'
"""
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TokenType(Enum):
    """Enumeration representing the supported token types."""
    ATOM = 1
    FACTOR = 2
    OPENING_BRACKET = 3
    CLOSING_BRACKET = 4
    EOF = 5


@dataclass
class Token:
    """Dataclass representing a token instance.

    Attributes:
        value: String value of the token.
        token_type: Type of the supported token.
    """
    value: str
    token_type: TokenType


class TokenizerException(Exception):
    """Exception raised by chemical_formula.tokenize function if given token
    is not supported.

    Args:
        token: The unsupported token.

    Attributes:
        token: The unsupported token.
        message (str): Human readable string describing the exception.
    """
    def __init__(self, token: str):
        self.token = token
        self.message = f"Invalid Token: {token}"
        super().__init__(self.message)


def tokenize(token: str) -> Token:
    """Creates a Token instance from a string.

    Args:
        token: String to tokenize.

    Returns:
        Token: Related Token instance.

    Raises:
        TokenizerException: If given token type is not supported (see enum TokenType).
    """
    if token == "":
        return Token(token, TokenType.EOF)
    if token.isalpha():
        return Token(token, TokenType.ATOM)
    if token.isdecimal():
        return Token(token, TokenType.FACTOR)
    if token in {'(', '{', '['}:
        return Token(token, TokenType.OPENING_BRACKET)
    if token in {')', '}', ']'}:
        return Token(token, TokenType.CLOSING_BRACKET)

    raise TokenizerException(token)


class Lexer:
    """This class can be used to retrieve the Token instances related to a chemical formula string.

    Args:
        formula: Chemical formula to tokenize.

    Attributes:
        position (int): Position of the last retrieved token.
    """
    def __init__(self, formula: str):
        self._tokens = re.findall(r'[A-Z][a-z]?|\d+|[\[({})\]]', formula)
        self.position = 0

    def peek(self) -> Token:
        """Returns next token. Token is not consumed.

        Returns:
            Token: Next token.
        """
        try:
            return tokenize(self._tokens[self.position])
        except IndexError:
            return tokenize("")

    def get_next_token(self) -> Token:
        """Returns next token. Token is consumed.

        Returns:
            Token: Next token.
        """
        token = self.peek()
        self.position += 1
        return token


class ParsingException(Exception):
    """If the chemical formula grammar is not respected, this exception is raised by
    chemical_formula.Parser.parse_formula().

    Args:
        token: The token related to the parsing error.
        position: Position where the parsing error occured.

    Attributes:
        token: The token related to the parsing error.
        position: Position where the parsing error occured.
        message (str): Human readable string describing the exception.
    """
    def __init__(self, token: Token, position: int):
        self.token = token
        self.position = position
        self.message = f"Invalid Token '{token.token_type}' at position {position}"
        super().__init__(self.message)


class Parser:
    """This class can be used to parse a chemical formula.

    Args:
        lexer: chemical_formula.Lexer instance. Needed to retrieve the tokens related to
        the chemical formula.
    """
    def __init__(self, lexer: Lexer):
        self._lexer = lexer
        self._result = None

    def parse_formula(self) -> Dict[str, int]:
        """Parses the chemical formula.

        Returns:
            A dict whose keys are the atoms found in the formula, and the values are
            the occurences number of these atoms.

        Raises:
            ParsingException: If the grammar related to the formula is not respected.
        """
        if self._result is None:
            self._result = dict(self._parse_molecule())
            token = self._lexer.peek()
            if token.token_type is not TokenType.EOF:
                raise ParsingException(token, self._lexer.position)
        return self._result

    def _parse_molecule(self) -> Counter:
        """Parses 'molecule' grammar rule.

        Returns:
            Counter: A dict whose keys are the atoms found in the molecule, and the values are
            the occurences number of these atoms.

        Raises:
            ParsingException: If the grammar related to molecule is not respected.
        """
        outer_counter = Counter()
        token = self._lexer.peek()
        if token.token_type in { TokenType.OPENING_BRACKET, TokenType.ATOM }:
            inner_counter = self._parse_group()
            outer_counter += inner_counter
        else:
            raise ParsingException(token, self._lexer.position)

        token = self._lexer.peek()
        if token.token_type in { TokenType.OPENING_BRACKET, TokenType.ATOM }:
            inner_counter = self._parse_molecule()
            outer_counter += inner_counter

        return outer_counter

    def _parse_group(self) -> Counter:
        """Parses 'group' grammar rule.

        Returns:
            Counter: A dict whose keys are the atoms found in the group, and the values are
            the occurences number of these atoms.

        Raises:
            ParsingException: If the grammar related to the group is not respected.
        """
        counter = Counter()
        token = self._lexer.peek()
        if token.token_type is TokenType.OPENING_BRACKET:
            self._consume_opening_bracket()
            counter = self._parse_molecule()
            self._consume_closing_bracket()
        elif token.token_type is TokenType.ATOM:
            counter = self._parse_atom()
        else:
            raise ParsingException(token, self._lexer.position)

        token = self._lexer.peek()
        if token.token_type is TokenType.FACTOR:
            factor = self._parse_factor()
            if factor != 1:
                for key in counter.keys():
                    counter[key] = counter[key] * factor

        return counter

    def _consume_opening_bracket(self) -> None:
        """Consumes opening bracket token. This method is called right after the token is checked,
        which is why the grammar is not checked here.
        """
        self._lexer.get_next_token()

    def _consume_closing_bracket(self) -> None:
        """Consumes closing bracket token.

        Raises:
            ParsingException: If the closing bracket is missing.
        """
        token = self._lexer.get_next_token()
        if token.token_type is not TokenType.CLOSING_BRACKET:
            raise ParsingException(token, self._lexer.position)

    def _parse_atom(self) -> Counter:
        """Parses the atom.

        Returns:
            Counter: A dict whose keys are the atoms found in the group, and the values are
            the occurences number of these atoms.
        """
        token = self._lexer.get_next_token()
        return Counter({token.value: 1})

    def _parse_factor(self) -> int:
        """Parses the factor. This method is called right after the token is checked, which is why
        the grammar is not checked here.
        """
        token = self._lexer.get_next_token()
        return int(token.value)
