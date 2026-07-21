#!/usr/bin/env python3
import sys
import json
import argparse


def tokenize(text):
    tokens = []
    i = 0
    n = len(text)
    bol = True

    while i < n:
        c = text[i]

        if c in ' \t':
            i += 1
            continue

        if c == '\n':
            bol = True
            i += 1
            continue

        if c == '\r':
            bol = True
            i += 1
            if i < n and text[i] == '\n':
                i += 1
            continue

        if c == '/' and i + 1 < n:
            if text[i + 1] == '/':
                end = text.find('\n', i)
                if end == -1:
                    end = n
                tokens.append(('C', text[i:end], bol))
                i = end
                bol = True
                continue
            if text[i + 1] == '*':
                end = text.find('*/', i + 2)
                if end == -1:
                    end = n
                else:
                    end += 2
                block = text[i:end]
                tokens.append(('C', block, bol))
                if '\n' in block:
                    bol = True
                i = end
                continue

        if c in '{}[],:':
            tokens.append(('P', c, bol))
            bol = False
            i += 1
            continue

        if c in '"\'':
            quote = c
            i += 1
            chars = []
            while i < n:
                if text[i] == '\\':
                    if i + 1 < n:
                        esc = text[i + 1]
                        i += 2
                        if esc == '"':
                            chars.append('"')
                        elif esc == "'":
                            chars.append("'")
                        elif esc == '\\':
                            chars.append('\\')
                        elif esc == 'n':
                            chars.append('\n')
                        elif esc == 'r':
                            chars.append('\r')
                        elif esc == 't':
                            chars.append('\t')
                        elif esc == 'b':
                            chars.append('\b')
                        elif esc == 'f':
                            chars.append('\f')
                        elif esc == 'v':
                            chars.append('\v')
                        elif esc == '0':
                            chars.append('\x00')
                        elif esc == '/':
                            chars.append('/')
                        elif esc == 'u' and i + 4 <= n:
                            chars.append(chr(int(text[i:i+4], 16)))
                            i += 4
                        elif esc == 'x' and i + 2 <= n:
                            chars.append(chr(int(text[i:i+2], 16)))
                            i += 2
                        else:
                            chars.append(esc)
                    else:
                        break
                elif text[i] == '\n':
                    chars.append('\n')
                    i += 1
                elif text[i] == '\r':
                    chars.append('\n')
                    i += 1
                    if i < n and text[i] == '\n':
                        i += 1
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    chars.append(text[i])
                    i += 1
            tokens.append(('S', ''.join(chars), bol))
            bol = False
            continue

        if c.isalpha() or c in '$_':
            start = i
            while i < n and (text[i].isalnum() or text[i] in '$_'):
                i += 1
            word = text[start:i]
            if word in ('true', 'false', 'null'):
                tokens.append(('K', word, bol))
            else:
                tokens.append(('I', word, bol))
            bol = False
            continue

        if c.isdigit() or c in '+-.':
            start = i
            i += 1
            while i < n and text[i] in '0123456789.eExXa-fA-F+-':
                if text[i] in '+-' and text[i - 1] not in 'eE':
                    break
                i += 1
            s = text[start:i]
            while s and s[-1] in 'eExX+-.':
                s = s[:-1]
                i -= 1
            if s:
                tokens.append(('N', s, bol))
                bol = False
            continue

        i += 1

    return tokens


def is_empty(tokens, idx):
    depth = 1
    for j in range(idx + 1, len(tokens)):
        tt, tv, _ = tokens[j]
        if tt == 'C':
            continue
        if tv in '{[':
            depth += 1
        elif tv in '}]':
            depth -= 1
            if depth == 0:
                return True
        else:
            return False
    return False


def find_close(tokens, idx):
    open_c = tokens[idx][1]
    close_c = '}' if open_c == '{' else ']'
    depth = 1
    j = idx + 1
    while j < len(tokens):
        _, tv, _ = tokens[j]
        if tv == open_c:
            depth += 1
        elif tv == close_c:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return j


def format_tokens(tokens, indent=4):
    out = []
    depth = 0
    fresh = True
    need_nl = False
    bol_next = False

    def indent_line():
        nonlocal fresh
        if fresh:
            out.append(' ' * indent * depth)
            fresh = False

    def nl():
        nonlocal fresh
        while out and out[-1] == ' ':
            out.pop()
        out.append('\n')
        fresh = True

    def strip_trail():
        while out and out[-1] in ('\n', ' '):
            out.pop()

    i = 0
    while i < len(tokens):
        tt, tv, bol = tokens[i]

        # ----- comment -----
        if tt == 'C':
            if bol or bol_next:
                bol_next = False
                if out and out[-1] != '\n':
                    nl()
                indent_line()
            else:
                out.append(' ')
            out.append(tv)
            if tv.startswith('//'):
                need_nl = False
                nl()
            elif '\n' in tv:
                need_nl = False
                nl()
            else:
                out.append(' ')
            i += 1
            continue

        # ----- open -----
        if tv in '{[':
            if is_empty(tokens, i):
                if need_nl:
                    nl()
                    indent_line()
                indent_line()
                out.append(tv + (']' if tv == '[' else '}'))
                i = find_close(tokens, i) + 1
                need_nl = True
                fresh = True
                continue
            if need_nl:
                nl()
                indent_line()
            else:
                indent_line()
            out.append(tv)
            depth += 1
            need_nl = False
            nl()
            bol_next = True
            i += 1
            continue

        # ----- close -----
        if tv in ']}':
            depth -= 1
            strip_trail()
            while out and out[-1] == ',':
                out.pop()
            nl()
            indent_line()
            out.append(tv)
            need_nl = True
            fresh = True
            i += 1
            continue

        # ----- colon -----
        if tv == ':':
            out.append(': ')
            need_nl = False
            i += 1
            continue

        # ----- comma -----
        if tv == ',':
            out.append(',')
            need_nl = True
            i += 1
            continue

        # ----- value (S, I, N, K) -----
        if need_nl:
            nl()

        if bol or bol_next:
            bol_next = False
            if out and out[-1] != '\n':
                nl()

        indent_line()

        if tt == 'S':
            out.append(json.dumps(tv))
        elif tt == 'I':
            out.append(json.dumps(tv))
        elif tt == 'N':
            out.append(tv)
        elif tt == 'K':
            out.append(tv)

        need_nl = True
        i += 1

    return ''.join(out)


def format_json5(text, indent=4):
    tokens = tokenize(text)
    return format_tokens(tokens, indent)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--indent', type=int, default=4)
    args = parser.parse_args()
    text = sys.stdin.read()
    result = format_json5(text, args.indent)
    sys.stdout.write(result + '\n')


if __name__ == '__main__':
    main()
