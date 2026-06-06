import re

style_tokens = [
    ('Token', r'[a-zA-Z0-9_.]+'),
    ('String', r'"([^\\"]*(\\.)?)*"'),
    ('Tag', r'<[a-zA-Z0-9_.]+>'),
    ('Set', r'\:\:='),
    ('Or', r'\|'),
    ('Many', r'\*'),
    ('To', r'->'),
    ('Number', r'[0-9]+'),
    ('OpenCurlyBracket', r'\{'),
    ('CloseCurlyBracket', r'\}'),
    ('OpenBracket', r'\('),
    ('CloseBracket', r'\)'),
    ('SemiColon', r';'),
    ('SKIP', r'(\s+)|(?:/\*(.*?)\*/)'),
]

style_groups = {
    "<File>": [{"multiple": "<Token>"}, {"multiple": "<Rule>"}],
    "<Token>": ["Token", "String"],
    "<Rule>": ["Tag", "Set", "<Value>", "SemiColon"],
    "<Value>": {"multiple": {"any": ["String", "Token", "Tag", "<Group>", "<Index>"]}},
    "<Group>": ["OpenBracket", "<Value>", {"multiple": ["Or", "<Value>"]}, "CloseBracket"],
    "<Index>": {"any": ['Many', ['OpenCurlyBracket', {"any": [['Number', 'To', 'Number'], 'Number']}, 'CloseBracket']]}
}

string = r"""
Token "[a-zA-Z0-9_.]+"
String "\"([^\\\"]*(\\.)?)*\""
Tag "<[a-zA-Z0-9_.!*-]+>"
Set "::="
Or "\|"
Many "\*"
To "->"
Number "[0-9]+"
OpenCurlyBracket "\{"
CloseCurlyBracket "\}"
OpenBracket "\("
CloseBracket "\)"
SemiColon ";"
SKIP "(\s+)|(?:/\*(.*?)\*/)"

<File> ::= <Token>* <Rule>* ;
<Token> ::= Token String ;
<Rule> ::= Tag Set <Value> SemiColon ;
<Value> ::= (String Token Tag <Group> <Index>)* ;
<Group> ::= OpenBracket <Value> (Or <Value>)* CloseBracket ;
<Index> ::= (Many | (OpenCurlyBracket ((Number To Number) | Number) CloseBracket)) ;
"""


class Token:
    """A simple data-structure for a token"""

    type: str
    value: str
    line: int
    char: int

    def __init__(self, type_, value, line, char, filename):
        self.type = type_
        self.value = value
        self.filename = filename
        self.line = line
        self.char = char

    def __repr__(self):
        return f"{self.type}[{repr(self.value)}]"


class Statement:
    """A simple data-structure for a statement"""

    name: str
    value: Token | list

    def __init__(self, name: str, value: Token | list):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}{repr(self.value)}"


def parse_statements(
        what: str,
        statement_spec: dict[str, str | list[...] | dict[str, int | str | list[...]]],
        tokens: list[Token]
) -> Token | Statement | list[...]:
    """
    Parse statements, grouping tokens under each statement name

    Parameters:
        what: str
            What statement to parse

        statement_spec: dict[str, str | list[...] | dict[str, int | str | list[...]]]
            The specifications for the statements

        tokens: list[Token]
            A list of parsed tokens

    Returns:
        A token, a statement or a list of these recursively
    """

    statements, index = peak_tokens(what, statement_spec, tokens, 0, 0)

    while index < len(tokens) and tokens[index].type == "SKIP":
        index += 1

    if statements is None or index != len(tokens):
        print(index, len(tokens), statements is None)
        raise SyntaxError(
            "Unexpected token %s at line %i chr %i: %s"
            % (tokens[index].type, tokens[index].line, tokens[index].char, repr(tokens[index].value))
        )

    return statements


def peak_tokens(
        what: str | list[...] | dict[str, ...],
        statement_spec: dict[str, str | list[...] | dict[str, int | str | list[...]]],
        tokens: list[Token], index: int,
        lv  # used for debugging purposes
) -> tuple[Token | Statement | list[Token | Statement | list[...]] | None, int]:
    """
    Parse statements, grouping tokens under each statement name
    Peaks into the structure to see if it can greedly consume `what` from the `statement_spec`

    Parameters:
        what: str | list[...] | dict[str, ...]
            What to greedly consume

        statement_spec: dict[str, str | list[...] | dict[str, int | str | list[...]]]
            The specifications for the statements

        tokens: list[Token]
            A list of parsed tokens

        lv: int
            Used for debugging purposes

    Returns:
        A tuple containing:
            A token, a statement or a list of these recursively
            The number of tokens consumed
    """

    # print("\t" * lv, "peak", what)

    if index >= len(tokens):
        # print("\t" * lv, "empty")
        return None, index

    if isinstance(what, str):
        if what in statement_spec:
            statements, consumed_tokens = peak_tokens(statement_spec[what], statement_spec, tokens, index, lv + 1)
            if statements is None:
                # print("\t" * lv, "not found Statement", what)
                return statements, consumed_tokens

            # print("\t" * lv, "found Statement", what)
            return Statement(what, statements), consumed_tokens

        # Ignore SKIP
        if what != "SKIP":
            # print("\t" * (lv + 1), "SKIP")
            while index < len(tokens) and tokens[index].type == "SKIP":
                index += 1

        if index >= len(tokens):
            # print("\t" * lv, "not found too long")
            return None, index

        if what == tokens[index].type:
            # print("\t" * lv, "found", tokens[index])
            return tokens[index], index + 1

        # print("\t" * lv, "not found", tokens[index])
        return None, index

    if isinstance(what, dict) and "multiple" in what:
        from_ = 0
        to = 0
        if "count" in what:
            from_ = what["count"]
            to = what["count"]
        elif "from" in what:
            from_ = what["from"]
        elif "to" in what:
            to = what["to"]

        item = what["multiple"]

        if to != 1:
            next_ = {"multiple": item, "from": max(from_ - 1, 0), "to": max(to - 1, 0)}
            statements, consumed_tokens = peak_tokens([item, next_], statement_spec, tokens, index, lv + 1)
            if statements is not None:
                array = [statements[0]] + statements[1]
                if len(array) < from_:
                    # print("\t" * lv, "not found multiple TOO LONG")
                    return None, consumed_tokens

                # print("\t" * lv, "found" if array else "not found", "multiple PEAK")
                return array, consumed_tokens

        statements, consumed_tokens = peak_tokens(item, statement_spec, tokens, index, lv + 1)
        if statements is None:
            if from_ == 0:
                # print("\t" * lv, "not found multiple END")
                return [], index

            # print("\t" * lv, "found multiple")
            return statements, consumed_tokens

        # print("\t" * lv, "found multiple one")
        return [statements], consumed_tokens

    elif isinstance(what, list):
        values = []
        for each_what in what:
            statements, consumed_tokens = peak_tokens(each_what, statement_spec, tokens, index, lv + 1)
            if statements is None:
                # print("\t" * lv, "not found list")
                return None, consumed_tokens

            values.append(statements)
            index = consumed_tokens

        # print("\t" * lv, "found" if values else "not found", "list")
        return values, index

    elif isinstance(what, dict) and "any" in what and isinstance(what["any"], list):
        for each_what in what["any"]:
            statements, consumed_tokens = peak_tokens(each_what, statement_spec, tokens, index, lv + 1)

            if statements:
                # print("\t" * lv, "found any")
                return statements, consumed_tokens

        # print("\t" * lv, "not found any")
        return None, index

    # We should never get here but still good to error
    raise Exception("Wrong type: " + str(type(what)))


def tokenize(
        string: str,
        token_spec: list[tuple[str, str | re.Pattern]],
        filename: str
) -> list[Token]:
    """
    Tokenize an input string

    Parameters:
        string: str
            The string to tokenize

        token_spec: list[tuple[str, str | re.Pattern]]
            The specifications for the tokens

        filename: str
            The filename to use for the tokens

    Returns:
        A list of tokens
    """

    start = 0
    tokens = []
    while start < len(string):
        match = None
        for token_name, token_regex in token_spec:
            match = re.match(token_regex, string[start:], re.MULTILINE | re.DOTALL)
            if match:
                break

        line = string[:start].count("\n")
        char = len(string[:start].rsplit("\n", 1)[-1])
        if not match:
            raise SyntaxError("Unexpected character %s at line %i chr %i" % (string[start], line, char))

        tokens.append(Token(token_name, match.group(), line, char, filename))

        start = start + match.end()

    return tokens


def pprint_statement_value(value: any, indent: int = 0):
    """Pretty Print a statement value"""

    indent_str = '\t' * indent

    if isinstance(value, Statement):
        pprint_statement(value, indent)

    elif isinstance(value, Token):
        print(f"{indent_str}{value}")

    elif isinstance(value, list):
        for statement in value:
            pprint_statement_value(statement, indent)
    else:
        raise TypeError("Unknown type: " + type(value))


def pprint_statement(statement: Statement, indent: int = 0):
    """Pretty Print a statement"""

    indent_str = '\t' * indent
    print(f"{indent_str}{statement.name}{{")
    pprint_statement_value(statement.value, indent + 1)
    print(f"{indent_str}}}")


if __name__ == "__main__":
    tokens = tokenize(string, style_tokens, "File")
    print(tokens)
    statements = parse_statements("<File>", style_groups, tokens)

    pprint_statement_value(statements)

    # @todo write parser
    # need a parser class + a `parse_file(string: str, filename: str)` func
