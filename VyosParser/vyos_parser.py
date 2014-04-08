#!/usr/bin/env python


import sys
# sys.settrace #used for debugging

import json
import re
from pprint import pprint

from codetalker.pgm import Grammar, Translator
from codetalker.pgm.nodes import ParseTree
from codetalker.pgm.special import star, plus, _or
from codetalker.pgm.tokens import *
from codetalker.cgrammar import ParseNode


# TODO
# Med: this regular expression is fragile because 
# charaters in HEADER are hard coded.

__all__ = [ 'decode_string', 'decode_string_to_json' ]
_any_header_re = r"([a-zA-Z0-9-_.:/'\"$]+)"
_dbl_quoted_string_re = r'("(?:[^"\n\r\\]|(?:"")|(?:\\x[0-9a-fA-F]+)|(?:\\.))*")'

class HEADER(ReToken):
    rx = re.compile(_dbl_quoted_string_re + "|" + _any_header_re) #don't change the order

def toplevel(rule):
    rule | (units)
    rule.astAttrs = { "units": units }
    rule.pass_single = True

toplevel.ast_name = 'Toplevel'

def units(rule):
    rule | plus(star(NEWLINE), unit, star(NEWLINE))
    rule.astAttrs = {"units": [unit]}

units.ast_name = 'Units'

def unit(rule):
    rule | (headers, body)
    rule.astAttrs =  { "headers": headers, "body": body }

unit.ast_name = 'Unit'

def headers(rule):
    rule | plus(HEADER)
    rule.astAttrs = {"headers": [HEADER]}

headers.ast_name = "Headers"

def body(rule):
    rule | ("{", [entries],  "}")
    rule.astAttrs = {"entries": entries}

body.ast_name = 'Body'

def entries(rule):
    rule | (star(NEWLINE), star(entry,plus(NEWLINE)))
    rule.astAttrs = {"entries": [ entry ]}

entries.ast_name = 'Entries'

def entry(rule):
    rule | (entry_head, [entry_tail])
    rule.astAttrs = {"entry_head": entry_head, "entry_tail": entry_tail}

entry.ast_name = 'Entry'

def entry_head(rule):
    rule | plus(HEADER)
    rule.astAttrs = { "headers": [HEADER] }

entry_head.ast_name = 'EntryHead'

def entry_tail(rule):
    rule | (body)
    rule.astAttrs = {"body": body}

entry_tail.ast_name = 'EntryTail'

# TODO
# Med: this is not perfect but at least functional

grammar = Grammar(start=toplevel,
        tokens=[HEADER, WHITE, NEWLINE, ANY],
        ignore=[WHITE],
        ast_tokens=[STRING])


Dict = Translator(grammar)
ast = grammar.ast_classes


@Dict.translates(ast.Toplevel)
def t_toplevel(node):
    return Dict.translate(node.units)

@Dict.translates(ast.Units)
def t_units(node):
    # return [ Dict.translate(unit) for unit in node.units ]
    return dict( Dict.translate(unit) for unit in node.units )

@Dict.translates(ast.Unit)
def t_unit(node):
    _headers = Dict.translate(node.headers)
    _body = Dict.translate(node.body)
    return (_headers, _body)

@Dict.translates(ast.Headers)
def t_headers(node):
    _headers = []
    for header in node.headers:
        _headers.append(Dict.translate(header))
    return " ".join(_headers)

@Dict.translates(ast.Body)
def t_body(node):
    return Dict.translate(node.entries)

# TODO
# Med: optimize this function without sacrificing readability

@Dict.translates(ast.Entries)
def t_entries(node):
    dict = {}
    for entry in node.entries:
        _x = Dict.translate(entry)
        if len(_x) == 1:
            _k, _v = _x[0], "enabled" #some entry have only on header (example ssh { allow-root })
        else:
            _k, _v = _x[0:2]
        if _k in dict:
            if isinstance(dict[_k], list):
                dict[_k].append(_v)
            else:
                dict[_k] = [dict[_k], _v]
        else:
            dict[_k] = _v
    return dict

@Dict.translates(ast.Entry)
def t_entry(node):
    _head = Dict.translate(node.entry_head)
    _tail = Dict.translate(node.entry_tail)
    if _tail == None:         # when we have `key value` (no body following)
        return _head
    _head = " ".join(_head)   # when we have `key { ... }`
    return [ _head, _tail ]

@Dict.translates(ast.EntryHead)
def t_entry_head(node):
    _headers = []
    for header in node.headers:
        _headers.append(Dict.translate(header))
    return _headers;

@Dict.translates(ast.EntryTail)
def t_entry_tail(node):
    if node.body != None:
        return Dict.translate(node.body)
    else:
        return None

@Dict.translates(HEADER)
def t_HEADER(node):
    return node.value

def _dict_to_json(hash):
    return json.dumps(hash, sort_keys=True, indent=2, separators=(',', ': '))

def _decode_string(string):
    return Dict.from_string(string)

## Public Interface ##
def decode_string(string):
    """This is the main function takes Vyos 
    output as string parameter
    and translates it into python dictionary """
    return _decode_string(string)
   
def decode_string_to_json(string):
    """Just a wrapper around decode_string_dict for convenience"""
    return _dict_to_json(_decode_string(string))



# vim: et sts=4:ts=4:sw=4
