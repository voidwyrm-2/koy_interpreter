from typing import Any



DIGITS = '0123456789'
ALPHABET_LOW = 'abcdefghijklmnopqrstuvwxyz'
ALPHABET_UPP = ALPHABET_LOW.upper()
VALID_FOR_IDENTS = ALPHABET_LOW + ALPHABET_UPP + '_'

TT_COMMENT = 'COMMENT'
TT_IMPORT = 'IMPORT'
TT_ASSIGN = 'ASSIGN'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_STRING = 'STRING'
TT_IDENT = 'IDENT'
TT_OPENING_OBJ = 'OPENING_OBJ'
TT_CLOSING_OBJ = 'CLOSING_OBJ'
TT_OPENING_ARR = 'OPENING_ARR'
TT_CLOSING_ARR = 'CLOSING_ARR'
TT_ARR_SEP = 'ARR_SEP'
TT_BOOL = 'BOOL'
TT_NULL = 'NULL'
TT_EOF = 'EOF'
TT_ILLEGAL = 'ILLEGAL'



class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile "{self.pos_start.fn}", line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'illegal character', details)

class InvaildSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'invaild syntax', details)

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'runtime error', details)


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        if current_char == '\n': self.ln += 1; self.col += 1

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None) -> None:
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self) -> str:
        if self.value: return f'{self.type}:{self.value}'
        return str(self.type)


# oh no pythonman's nemesis
class Lexer:
    def __init__(self,fn, text):
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def make_tokens(self):
        tokens: list[Token] = []

        while self.current_char != None:
            #print(self.current_char)
            if self.current_char in ' \t' or self.current_char == '\n': self.advance()
            elif self.current_char == '/': tokens.append(self.make_comment())
            elif self.current_char in DIGITS: tokens.append(self.make_number())
            elif self.current_char in VALID_FOR_IDENTS: tokens.append(self.make_ident())
            elif self.current_char == '"': tokens.append(self.make_string())
            elif self.current_char == ':': tokens.append(Token(TT_ASSIGN, pos_start=self.pos)); self.advance()
            elif self.current_char == '{': tokens.append(Token(TT_OPENING_OBJ, pos_start=self.pos)); self.advance()
            elif self.current_char == '}': tokens.append(Token(TT_CLOSING_OBJ, pos_start=self.pos)); self.advance()
            elif self.current_char == '[': tokens.append(Token(TT_OPENING_ARR, pos_start=self.pos)); self.advance()
            elif self.current_char == ']': tokens.append(Token(TT_CLOSING_ARR, pos_start=self.pos)); self.advance()
            elif self.current_char == ',': tokens.append(Token(TT_ARR_SEP, pos_start=self.pos)); self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f'\'{char}\'')

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1; num_str += '.'
            else: num_str += self.current_char
            self.advance()

        if dot_count == 0: return Token(TT_INT, int(num_str), pos_start, self.pos)
        return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
    
    def make_string(self):
        string_str = ''
        pos_start = self.pos.copy()
        self.advance()

        while self.current_char != None and self.current_char != '"':
            string_str += self.current_char
            self.advance()
        self.advance()
        return Token(TT_STRING, string_str, pos_start, self.pos)

    def make_comment(self):
        comment_str = ''
        pos_start = self.pos.copy()

        self.advance()

        block_comment = False

        if self.current_char == '/': self.advance()
        elif self.current_char == '*': block_comment = True; self.advance()
        else: return Token(TT_ILLEGAL, None, pos_start, self.pos)

        while self.current_char != None:
            if self.current_char == '*' and block_comment:
                self.advance()
                if self.current_char == '/': break
                else: comment_str += '*'; comment_str += self.current_char
            elif self.current_char == '\n' and not block_comment: break
            else: comment_str += self.current_char
            self.advance()

        return Token(TT_COMMENT, comment_str, pos_start, self.pos)

    def make_ident(self):
        ident_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in VALID_FOR_IDENTS:
            ident_str += self.current_char
            self.advance()

        ident = self.check_keyword(ident_str)

        if ident == TT_BOOL: ident_str = bool(ident_str)
        elif ident != TT_IDENT: ident_str = None

        return Token(ident, ident_str, pos_start, self.pos)
    
    def check_keyword(self, word: str):
        match word:
            case 'import': return TT_IMPORT
            case 'true' | 'false': return TT_BOOL
            case 'null': return TT_NULL
            case x: return TT_IDENT



class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self): return str(self.tok)

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    
    def register(self, res): 
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
    
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
    
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvaildSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "expected '+', '-', '*', or '/' but got end of file instead"))
        return res

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else: return res.failure(InvaildSyntaxError(tok.pos_start, tok.pos_end, 'expected \')\''))

        elif tok.type == TT_LESSERTHAN:
            pass

        return res.failure(InvaildSyntaxError(tok.pos_start, tok.pos_end, 'expected int or float'))

    def term(self):
        return self.bin_op(self.factor, ())

    def expr(self):
        return self.bin_op(self.term, ())

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)




class RuntimeResult:
    def __init__(self):
        self.error = None
        self.value = None
    
    '''def register(self, res):
        print('at RuntimeResult.register!')
        if isinstance(res, ParseResult):
            print('is instance!')
            if res.error: self.error = res.error
            print(f'res.value: "{res.value}"')
            return res.value
        else: print('not instance!')'''
    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

class Boolean:
    def __init__(self, value: bool):
        self.value = value
        self.set_pos()
    
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def __repr__(self): return str(self.value)

class Number:
    def __init__(self, value: int):
        self.value = value
        self.set_pos()
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def __repr__(self): return str(self.value)

class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self): return str(self.tok)


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        #print('name: "' + type(node).__name__ + '"')
        return method(node, context)

    def no_visit_method(self, node, context): raise Exception(f'no visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node, context):
        #print('found number node')
        return RuntimeResult().success(Number(node.tok.value).set_pos(node.pos_start, node.pos_end))

    def visit_BooleanNode(self, node, context):
        #print('found number node')
        return RuntimeResult().success(Boolean(node.tok.value).set_pos(node.pos_start, node.pos_end))



def run(fn, text):
    # generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    #print(tokens)
    if error: return None, error
    
    # generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    # interpret AST
    interpreter = Interpreter()
    context = Context('<program>')
    #print(ast.node)
    result = interpreter.visit(ast.node, context)

    return result.value, result.error