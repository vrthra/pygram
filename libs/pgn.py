# pgn.py rel. 1.1 17-sep-2004
#
# Demonstration of the parsing module, implementing a pgn parser.
#
# The aim of this parser is not to support database application,
# but to create automagically a pgn annotated reading the log console file
# of a lecture of ICC (Internet Chess Club), saved by Blitzin.
# Of course you can modify the Abstract Syntax Tree to your purpose.
#
# Copyright 2004, by Alberto Santini http://www.albertosantini.it/chess/
#
from pyparsing import alphanums, nums, quotedString
from pyparsing import Combine, Forward, Group, Literal, oneOf, OneOrMore, Optional, Suppress, ZeroOrMore, White, Word
from pyparsing import ParseException

#
# define pgn grammar
#

tag = Suppress("[") + Word(alphanums) + Combine(quotedString) + Suppress("]")
comment = Suppress("{") + Word(alphanums + " ") + Suppress("}")

dot = Literal(".")
piece = oneOf("K Q B N R")
file_coord = oneOf("a b c d e f g h")
rank_coord = oneOf("1 2 3 4 5 6 7 8")
capture = oneOf("x :")
promote = Literal("=")
castle_queenside = Literal("O-O-O") | Literal("0-0-0") | Literal("o-o-o")
castle_kingside = Literal("O-O") | Literal("0-0") | Literal("o-o")

move_number = Optional(comment) + Word(nums) + dot
m1 = file_coord + rank_coord # pawn move e.g. d4
m2 = file_coord + capture + file_coord + rank_coord # pawn capture move e.g. dxe5
m3 = file_coord + "8" + promote + piece # pawn promotion e.g. e8=Q
m4 = piece + file_coord + rank_coord # piece move e.g. Be6
m5 = piece + file_coord + file_coord + rank_coord # piece move e.g. Nbd2
m6 = piece + rank_coord + file_coord + rank_coord # piece move e.g. R4a7
m7 = piece + capture + file_coord + rank_coord # piece capture move e.g. Bxh7
m8 = castle_queenside | castle_kingside # castling e.g. o-o

check = oneOf("+ ++")
mate = Literal("#")
annotation = Word("!?", max=2)
nag = " $" + Word(nums)
decoration = check | mate | annotation | nag

variant = Forward()
half_move = Combine((m3 | m1 | m2 | m4 | m5 | m6 | m7 | m8) + Optional(decoration)) \
  + Optional(comment) +Optional(variant)
move = Suppress(move_number) + half_move + Optional(half_move)
variant << "(" + OneOrMore(move) + ")"
# grouping the plies (half-moves) for each move: useful to group annotations, variants...
# suggested by Paul McGuire :)
move = Group(Suppress(move_number) + half_move + Optional(half_move))
variant << Group("(" + OneOrMore(move) + ")")
game_terminator = oneOf("1-0 0-1 1/2-1/2 *")

pgnGrammar = Suppress(ZeroOrMore(tag))  + ZeroOrMore(move) + Suppress(game_terminator)

def parsePGN( pgn, bnf=pgnGrammar, fn=None ):
  try:
    return bnf.parseString( pgn )
  except ParseException, err:
    print err.line
    print " "*(err.column-1) + "^"
    print err

