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
    rx = re.compile(_dbl_quoted_string_re + "|" + _any_header_re) # don't change the order

def toplevel(rule):
    rule | (units)
    rule.astAttrs = { "units": units }
    rule.pass_single = True
toplevel.ast_name = 'Toplevel'

def units(rule):
    rule | plus(star(NEWLINE), [unit], star(NEWLINE))
    rule.astAttrs = {"units": [unit]}
units.ast_name = 'Units'

def unit(rule):
    rule | _or(dble_header_body , header_header, header_body, single_header)
    rule.astAttrs = { "t1": header_header, "t2": header_body, "t3": dble_header_body, "t4": single_header }
unit.ast_name = 'Unit'

def single_header(rule):
    rule | HEADER
    rule.astAttrs = { "header": HEADER }
single_header.ast_name = 'SingleHeader'

def header_header(rule):
    rule | (HEADER, HEADER)
    # rule | (HEADER, HEADER)
    rule.astAttrs = { "headers": [HEADER] }
header_header.ast_name = 'HeaderHeader'

def header_body(rule):
    rule | (HEADER, body)
    rule.astAttrs = { "header": HEADER, "body": body }
header_body.ast_name = 'HeaderBody'

def dble_header_body(rule):
    rule | (HEADER, HEADER, body)
    rule.astAttrs = { "headers": [HEADER], "body": body }
dble_header_body.ast_name = 'DbleHeaderBody'

def body(rule):
    rule | ("{", units,  "}")
    rule.astAttrs = { "units": units }
body.ast_name = 'Body'

grammar = Grammar(start=toplevel,
        tokens=[HEADER, WHITE, NEWLINE, ANY],
        ignore=[WHITE],
        ast_tokens=[STRING])

Dict = Translator(grammar)
ast = grammar.ast_classes

@Dict.translates(ast.Toplevel)
def t_toplevel():
    return Dict.translate(node.units)

@Dict.translates(ast.Units)
def t_units(node):
    dic = {}
    # h1, h2, b = None, None, None
    for unit in node.units:
        tu = Dict.translate(unit)
        typ = tu[0]
        if typ == "t1": # HeaderHeader
            k, v = tu[1:]
            if k in dic:
                if isinstance(dic[k], list):
                    dic[k].append(v)
                else:
                    dic[k] = [dic[k], v]
            else:
                dic[k] = v

        elif typ == "t2": # HeaderBody
            k, b = tu[1:]
            if k in dic:
                if isinstance(dic[k], list):
                    dic[k].append(b)
                else:
                    dic[k] = [dic[k], b]
            else:
                dic[k] = b

        elif typ == "t3": #DbleHeaderBody
            k1, k2, b = tu[1:]
            if not k1 in dic:
                dic[k1] = {}
            dic[k1][k2] = b

    return dic

@Dict.translates(ast.Unit)
def t_unit(node):
    if node.t1:
        return Dict.translate(node.t1)
    elif node.t2:
        return Dict.translate(node.t2)
    elif node.t3:
        return Dict.translate(node.t3)
    elif node.t4:
        return Dict.translate(node.t4)

@Dict.translates(ast.SingleHeader)
def t_single_header(node):
    return ["t1", Dict.translate(node.header), "on"]

@Dict.translates(ast.HeaderHeader)
def t_header_header(node):
    h1 = Dict.translate(node.headers[0])
    h2 = Dict.translate(node.headers[1])
    return ["t1", h1, h2]

@Dict.translates(ast.HeaderBody)
def t_header_body(node):
    h = Dict.translate(node.header)
    return ["t2", h, Dict.translate(node.body)]

@Dict.translates(ast.DbleHeaderBody)
def t_dble_header_body(node):
    h1 = Dict.translate(node.headers[0])
    h2 = Dict.translate(node.headers[1])
    return ["t3", h1, h2, Dict.translate(node.body)]

@Dict.translates(ast.Body)
def t_body(node):
    return Dict.translate(node.units)

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
