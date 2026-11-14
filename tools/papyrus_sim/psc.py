"""Reads Papyrus source (the Fallout 4 dialect) into a tree.

Only the part of the language this project's scripts use is understood:
script header, properties (Auto), groups, script variables, functions and
events, If / While / Return, assignment, calls, casts, arrays by index and
arrays made with "new". A
construct outside that part stops the parse with the file and line, so a
script cannot slip through half-read.

This is NOT the game's compiler. A script that parses here can still be
rejected by the real one.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class PapyrusSyntaxError(Exception):
    pass


# ------------------------------------------------------------------ lexer

@dataclass
class Tok:
    kind: str          # id | int | float | str | op | nl | eof
    text: str
    line: int
    value: Any = None

    @property
    def low(self) -> str:
        return self.text.lower()


OPERATORS = ["==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=",
             "+", "-", "*", "/", "%", "=", "<", ">", "!", "(", ")", "[", "]", ",", "."]


def lex(text: str, name: str = "<source>") -> List[Tok]:
    toks: List[Tok] = []
    i, n, line = 0, len(text), 1

    def err(msg):
        raise PapyrusSyntaxError("%s:%d: %s" % (name, line, msg))

    while i < n:
        c = text[i]
        if c == "\n":
            toks.append(Tok("nl", "\n", line))
            line += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif c == "\\":
            # line continuation: a backslash, then the end of the line
            j = i + 1
            while j < n and text[j] in " \t\r":
                j += 1
            if j < n and text[j] == "\n":
                line += 1
                i = j + 1
            else:
                err("stray backslash")
        elif c == ";":
            if text.startswith(";/", i):
                end = text.find("/;", i + 2)
                if end < 0:
                    err("block comment is never closed")
                line += text.count("\n", i, end)
                i = end + 2
            else:
                while i < n and text[i] != "\n":
                    i += 1
        elif c == "{":
            end = text.find("}", i)
            if end < 0:
                err("documentation comment is never closed")
            line += text.count("\n", i, end)
            i = end + 1
        elif c == '"':
            j = i + 1
            out = []
            while True:
                if j >= n or text[j] == "\n":
                    err("string is never closed")
                ch = text[j]
                if ch == "\\":
                    nxt = text[j + 1] if j + 1 < n else ""
                    out.append({"n": "\n", "t": "\t", "\\": "\\", '"': '"'}.get(nxt, "\\" + nxt))
                    j += 2
                    continue
                if ch == '"':
                    break
                out.append(ch)
                j += 1
            toks.append(Tok("str", text[i:j + 1], line, "".join(out)))
            i = j + 1
        elif c.isdigit() or (c == "." and i + 1 < n and text[i + 1].isdigit()):
            j = i
            if text.startswith(("0x", "0X"), i):
                j = i + 2
                while j < n and text[j] in "0123456789abcdefABCDEF":
                    j += 1
                toks.append(Tok("int", text[i:j], line, int(text[i:j], 16)))
            else:
                while j < n and text[j].isdigit():
                    j += 1
                is_float = False
                if j < n and text[j] == "." and j + 1 < n and text[j + 1].isdigit():
                    is_float = True
                    j += 1
                    while j < n and text[j].isdigit():
                        j += 1
                word = text[i:j]
                toks.append(Tok("float", word, line, float(word)) if is_float else Tok("int", word, line, int(word)))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            # a namespace: TLM:SelfTest
            while j + 1 < n and text[j] == ":" and (text[j + 1].isalpha() or text[j + 1] == "_"):
                j += 1
                while j < n and (text[j].isalnum() or text[j] == "_"):
                    j += 1
            toks.append(Tok("id", text[i:j], line))
            i = j
        else:
            for op in OPERATORS:
                if text.startswith(op, i):
                    toks.append(Tok("op", op, line))
                    i += len(op)
                    break
            else:
                err("unexpected character %r" % c)
    toks.append(Tok("nl", "\n", line))
    toks.append(Tok("eof", "", line))
    return toks


# ------------------------------------------------------------------- tree

@dataclass
class Param:
    type: str
    name: str
    default: Any = None          # an expression node, or None for "no default"
    has_default: bool = False


@dataclass
class Function:
    name: str
    return_type: Optional[str]
    params: List[Param]
    body: List[tuple]
    is_event: bool
    line: int
    flags: List[str] = field(default_factory=list)


@dataclass
class Property:
    type: str
    name: str
    default: Any                 # an expression node or None
    flags: List[str]
    line: int


@dataclass
class Variable:
    type: str
    name: str
    init: Any                    # an expression node or None
    const: bool
    line: int


@dataclass
class Script:
    name: str
    parent: str
    path: str
    properties: Dict[str, Property] = field(default_factory=dict)   # by lower-case name
    variables: Dict[str, Variable] = field(default_factory=dict)
    functions: Dict[str, Function] = field(default_factory=dict)


PRIMITIVES = {"int", "float", "bool", "string", "var"}
PROPERTY_FLAGS = {"auto", "autoreadonly", "const", "mandatory", "hidden", "conditional"}
FUNCTION_FLAGS = {"global", "native", "debugonly", "betaonly"}
ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%="}
STATEMENT_ENDERS = {"endif", "else", "elseif", "endwhile", "endfunction", "endevent"}


class Parser:
    def __init__(self, toks: List[Tok], name: str):
        self.toks = toks
        self.i = 0
        self.name = name

    # ---- token helpers
    @property
    def tok(self) -> Tok:
        return self.toks[self.i]

    def peek(self, k: int = 1) -> Tok:
        return self.toks[min(self.i + k, len(self.toks) - 1)]

    def err(self, msg, tok: Optional[Tok] = None):
        tok = tok or self.tok
        raise PapyrusSyntaxError("%s:%d: %s (at %r)" % (self.name, tok.line, msg, tok.text))

    def next(self) -> Tok:
        t = self.tok
        self.i += 1
        return t

    def is_word(self, word: str, tok: Optional[Tok] = None) -> bool:
        tok = tok or self.tok
        return tok.kind == "id" and tok.low == word

    def is_op(self, op: str, tok: Optional[Tok] = None) -> bool:
        tok = tok or self.tok
        return tok.kind == "op" and tok.text == op

    def expect_word(self, word: str) -> Tok:
        if not self.is_word(word):
            self.err("expected %s" % word)
        return self.next()

    def expect_op(self, op: str) -> Tok:
        if not self.is_op(op):
            self.err("expected %r" % op)
        return self.next()

    def expect_id(self) -> Tok:
        if self.tok.kind != "id":
            self.err("expected a name")
        return self.next()

    def skip_newlines(self):
        while self.tok.kind == "nl":
            self.i += 1

    def end_of_line(self):
        if self.tok.kind not in ("nl", "eof"):
            self.err("expected the end of the line")
        self.skip_newlines()

    def type_at(self, k: int = 0) -> Optional[Tuple[str, int]]:
        """If a type starts k tokens ahead, its text and how many tokens it takes."""
        t = self.peek(k)
        if t.kind != "id":
            return None
        if self.is_op("[", self.peek(k + 1)) and self.is_op("]", self.peek(k + 2)):
            return t.text + "[]", 3
        return t.text, 1

    # ---- script level
    def parse_script(self, path: str) -> Script:
        self.skip_newlines()
        self.expect_word("scriptname")
        name = self.expect_id().text
        parent = ""
        if self.is_word("extends"):
            self.next()
            parent = self.expect_id().text
        while self.tok.kind == "id":         # flags: Hidden, Conditional, Const ...
            self.next()
        self.end_of_line()
        script = Script(name, parent, path)
        while self.tok.kind != "eof":
            self.parse_top_level(script)
            self.skip_newlines()
        return script

    def parse_top_level(self, script: Script):
        t = self.tok
        if self.is_word("group"):
            self.next()
            self.expect_id()
            while self.tok.kind == "id":
                self.next()
            self.end_of_line()
            while not self.is_word("endgroup"):
                if self.tok.kind == "eof":
                    self.err("Group is never closed", t)
                self.parse_top_level(script)
                self.skip_newlines()
            self.next()
            self.end_of_line()
            return
        if self.is_word("function") or self.is_word("event"):
            self.parse_function(script, None)
            return
        if t.kind == "id" and t.low in ("import", "state", "auto", "struct", "customevent", "endstate"):
            self.err("this part of the language is not understood here")
        ty = self.type_at()
        if not ty:
            self.err("expected a declaration")
        type_text, width = ty
        after = self.peek(width)
        if self.is_word("function", after):
            self.i += width
            self.parse_function(script, type_text)
            return
        if self.is_word("property", after):
            self.i += width + 1
            name = self.expect_id()
            default = None
            if self.is_op("="):
                self.next()
                default = self.parse_expr()
            flags = []
            while self.tok.kind == "id" and self.tok.low in PROPERTY_FLAGS:
                flags.append(self.next().low)
            if "auto" not in flags and "autoreadonly" not in flags:
                self.err("only Auto properties are understood here", name)
            self.end_of_line()
            if name.low in script.properties or name.low in script.variables:
                self.err("%s is declared twice" % name.text, name)
            script.properties[name.low] = Property(type_text, name.text, default, flags, name.line)
            return
        # a script variable
        self.i += width
        name = self.expect_id()
        init = None
        if self.is_op("="):
            self.next()
            init = self.parse_expr()
        const = False
        while self.tok.kind == "id" and self.tok.low in ("const", "conditional", "hidden"):
            const = const or self.tok.low == "const"
            self.next()
        self.end_of_line()
        if name.low in script.properties or name.low in script.variables:
            self.err("%s is declared twice" % name.text, name)
        script.variables[name.low] = Variable(type_text, name.text, init, const, name.line)

    def parse_function(self, script: Script, return_type: Optional[str]):
        head = self.next()
        is_event = head.low == "event"
        name = self.expect_id()
        self.expect_op("(")
        params: List[Param] = []
        while not self.is_op(")"):
            ty = self.type_at()
            if not ty:
                self.err("expected a parameter type")
            self.i += ty[1]
            pname = self.expect_id()
            p = Param(ty[0], pname.text)
            if self.is_op("="):
                self.next()
                p.default = self.parse_expr()
                p.has_default = True
            params.append(p)
            if self.is_op(","):
                self.next()
            elif not self.is_op(")"):
                self.err("expected , or )")
        self.next()
        flags = []
        while self.tok.kind == "id" and self.tok.low in FUNCTION_FLAGS:
            flags.append(self.next().low)
        self.end_of_line()
        closer = "endevent" if is_event else "endfunction"
        if "native" in flags:
            body = []
        else:
            body = self.parse_block({closer})
            self.expect_word(closer)
            self.end_of_line()
        if name.low in script.functions:
            self.err("%s is defined twice" % name.text, name)
        script.functions[name.low] = Function(name.text, return_type, params, body, is_event, name.line, flags)

    # ---- statements
    def parse_block(self, closers) -> List[tuple]:
        body = []
        self.skip_newlines()
        while not (self.tok.kind == "id" and self.tok.low in closers):
            if self.tok.kind == "eof":
                self.err("block is never closed (expected %s)" % " or ".join(sorted(closers)))
            if self.tok.kind == "id" and self.tok.low in STATEMENT_ENDERS:
                self.err("unexpected %s" % self.tok.text)
            body.append(self.parse_statement())
            self.skip_newlines()
        return body

    def parse_statement(self) -> tuple:
        t = self.tok
        if self.is_word("if"):
            self.next()
            branches = []
            cond = self.parse_expr()
            self.end_of_line()
            body = self.parse_block({"elseif", "else", "endif"})
            branches.append((cond, body))
            otherwise = None
            while True:
                if self.is_word("elseif"):
                    self.next()
                    cond = self.parse_expr()
                    self.end_of_line()
                    branches.append((cond, self.parse_block({"elseif", "else", "endif"})))
                elif self.is_word("else"):
                    self.next()
                    self.end_of_line()
                    otherwise = self.parse_block({"endif"})
                    self.expect_word("endif")
                    break
                else:
                    self.expect_word("endif")
                    break
            self.end_of_line()
            return ("if", branches, otherwise, t.line)
        if self.is_word("while"):
            self.next()
            cond = self.parse_expr()
            self.end_of_line()
            body = self.parse_block({"endwhile"})
            self.expect_word("endwhile")
            self.end_of_line()
            return ("while", cond, body, t.line)
        if self.is_word("return"):
            self.next()
            value = None
            if self.tok.kind not in ("nl", "eof"):
                value = self.parse_expr()
            self.end_of_line()
            return ("return", value, t.line)
        # a local declaration: Type name [= expr]
        ty = self.type_at()
        if ty and self.peek(ty[1]).kind == "id" and not self.is_word("as", self.peek(ty[1])):
            self.i += ty[1]
            name = self.expect_id()
            init = None
            if self.is_op("="):
                self.next()
                init = self.parse_expr()
            self.end_of_line()
            return ("var", ty[0], name.text, init, t.line)
        left = self.parse_expr()
        if self.tok.kind == "op" and self.tok.text in ASSIGN_OPS:
            op = self.next().text
            if left[0] not in ("id", "member", "index"):
                self.err("cannot assign to this", t)
            right = self.parse_expr()
            self.end_of_line()
            return ("assign", left, op, right, t.line)
        if left[0] != "call":
            self.err("this line does nothing", t)
        self.end_of_line()
        return ("expr", left, t.line)

    # ---- expressions, lowest precedence first
    def parse_expr(self) -> tuple:
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.is_op("||"):
            line = self.next().line
            left = ("binary", "||", left, self.parse_and(), line)
        return left

    def parse_and(self):
        left = self.parse_compare()
        while self.is_op("&&"):
            line = self.next().line
            left = ("binary", "&&", left, self.parse_compare(), line)
        return left

    def parse_compare(self):
        left = self.parse_add()
        while self.tok.kind == "op" and self.tok.text in ("==", "!=", "<", ">", "<=", ">="):
            op = self.next()
            left = ("binary", op.text, left, self.parse_add(), op.line)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.tok.kind == "op" and self.tok.text in ("+", "-"):
            op = self.next()
            left = ("binary", op.text, left, self.parse_mul(), op.line)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.tok.kind == "op" and self.tok.text in ("*", "/", "%"):
            op = self.next()
            left = ("binary", op.text, left, self.parse_unary(), op.line)
        return left

    def parse_unary(self):
        if self.tok.kind == "op" and self.tok.text in ("-", "!"):
            op = self.next()
            return ("unary", op.text, self.parse_unary(), op.line)
        return self.parse_cast()

    def parse_cast(self):
        left = self.parse_postfix()
        while self.is_word("as"):
            line = self.next().line
            ty = self.type_at()
            if not ty:
                self.err("expected a type after 'as'")
            self.i += ty[1]
            left = ("cast", left, ty[0], line)
        return left

    def parse_args(self) -> List[Tuple[Optional[str], tuple]]:
        args = []
        while not self.is_op(")"):
            name = None
            if self.tok.kind == "id" and self.is_op("=", self.peek()) and not self.is_op("==", self.peek()):
                name = self.next().text
                self.next()
            args.append((name, self.parse_expr()))
            if self.is_op(","):
                self.next()
            elif not self.is_op(")"):
                self.err("expected , or )")
        self.next()
        return args

    def parse_postfix(self):
        t = self.tok
        if self.is_op("("):
            self.next()
            node = self.parse_expr()
            self.expect_op(")")
        elif t.kind in ("int", "float", "str"):
            self.next()
            node = ("lit", t.value, t.line)
        elif t.kind == "id":
            self.next()
            if t.low == "true":
                node = ("lit", True, t.line)
            elif t.low == "false":
                node = ("lit", False, t.line)
            elif t.low == "none":
                node = ("lit", None, t.line)
            elif t.low == "new":
                # new float[10], new Actor[count]: an array of that many defaults
                element = self.expect_id()
                self.expect_op("[")
                size = self.parse_expr()
                self.expect_op("]")
                return ("new", element.text, size, t.line)
            elif self.is_op("("):
                self.next()
                node = ("call", None, t.text, self.parse_args(), t.line)
            else:
                node = ("id", t.text, t.line)
        else:
            self.err("expected a value")
        while True:
            if self.is_op("."):
                self.next()
                name = self.expect_id()
                if self.is_op("("):
                    self.next()
                    node = ("call", node, name.text, self.parse_args(), name.line)
                else:
                    node = ("member", node, name.text, name.line)
            elif self.is_op("["):
                line = self.next().line
                idx = self.parse_expr()
                self.expect_op("]")
                node = ("index", node, idx, line)
            else:
                return node


def parse_file(path) -> Script:
    path = Path(path)
    text = path.read_text()
    return Parser(lex(text, path.name), path.name).parse_script(str(path))


def parse_folder(folder) -> Dict[str, Script]:
    """Every script in the folder, by lower-case script name."""
    scripts = {}
    for p in sorted(Path(folder).glob("*.psc")):
        s = parse_file(p)
        scripts[s.name.lower()] = s
    return scripts
