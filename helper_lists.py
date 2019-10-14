# !/usr/bin/python3
# By Sam Slate, 2019. Released to the public domain.
#
# Based on A.W. Appel, G.J. Jacobson, The world's fastest Scrabble program Comm. ACM, 31 (5) (1988), pp. 572-578
#
# Uses dawg implementation by Steve Hanov at http://stevehanov.ca/blog/?id=115

SCRABBLE_HEIGHT = 15
SCRABBLE_WIDTH = 15

DOUBLE_LETTER = "dl"
TRIPLE_LETTER = "tl"
DOUBLE_WORD = "dw"
TRIPLE_WORD = "tw"

BLANK = "*"

DICTIONARY = "dict.txt"

SCRABBLE_BINGO_BONUS = 50

current_rack = ["c", "a", "t", "c", "e", "r"]
current_rack_1 = ["a", "v", "e", "r", "f", "u", "m"]

placed_tiles_1 = {
	(5, 7): "c",
	(6, 7): "o",
	(7, 7): "a",
	(8, 7): "t"
	# (5, 9): "o",
	# (4, 9): "h",
	# (0, 3): "b",
	# (0, 2): "e",
	# (1, 3): "a",
	# (2, 4): "l",
	# (7, 7): "f"
}

placed_tiles = {
	(4, 7): "a",
	(5, 7): "f",
	(6, 7): "t",
	(7, 7): "e",
	(8, 7): "r",
	(8, 5): "h",
	(8, 6): "a",
	(8, 8): "d"
}

blank_board = {}

SCRABBLE_BONUS_PLACEMENTS = {
		(0,0): TRIPLE_WORD, (7, 0): TRIPLE_WORD, (14,0): TRIPLE_WORD, (0, 7): TRIPLE_WORD, 
		(14, 7): TRIPLE_WORD, (0, 14): TRIPLE_WORD, (7, 14): TRIPLE_WORD, (14,14): TRIPLE_WORD,
        (1,1): DOUBLE_WORD, (2,2): DOUBLE_WORD, (3,3): DOUBLE_WORD, (4,4): DOUBLE_WORD, (7, 7): DOUBLE_WORD,
        (1, 13): DOUBLE_WORD, (2, 12): DOUBLE_WORD, (3, 11): DOUBLE_WORD, (4, 10): DOUBLE_WORD, 
        (13, 1): DOUBLE_WORD, (12, 2): DOUBLE_WORD, (11, 3): DOUBLE_WORD, (10, 4): DOUBLE_WORD, 
        (13,13): DOUBLE_WORD, (12, 12): DOUBLE_WORD, (11,11): DOUBLE_WORD, (10,10): DOUBLE_WORD,
        (1,5): TRIPLE_LETTER, (1, 9): TRIPLE_LETTER, (5,1): TRIPLE_LETTER, (5,5): TRIPLE_LETTER, 
        (5,9): TRIPLE_LETTER, (5,13): TRIPLE_LETTER, (9,1): TRIPLE_LETTER, (9,5): TRIPLE_LETTER, 
        (9,9): TRIPLE_LETTER, (9,13): TRIPLE_LETTER, (13, 5): TRIPLE_LETTER, (13,9): TRIPLE_LETTER,
        (0, 3): DOUBLE_LETTER, (0,11): DOUBLE_LETTER, (2,6): DOUBLE_LETTER, (2,8): DOUBLE_LETTER, 
        (3,0): DOUBLE_LETTER, (3,7): DOUBLE_LETTER, (3,14): DOUBLE_LETTER, (6,2): DOUBLE_LETTER, 
        (6,6): DOUBLE_LETTER, (6,8): DOUBLE_LETTER, (6,12): DOUBLE_LETTER, (7,3): DOUBLE_LETTER, 
        (7,11): DOUBLE_LETTER, (8,2): DOUBLE_LETTER, (8,6): DOUBLE_LETTER, (8,8): DOUBLE_LETTER, 
        (8, 12): DOUBLE_LETTER, (11,0): DOUBLE_LETTER, (11,7): DOUBLE_LETTER, (11,14): DOUBLE_LETTER, 
        (12,6): DOUBLE_LETTER, (12,8): DOUBLE_LETTER, (14, 3): DOUBLE_LETTER, (14, 11): DOUBLE_LETTER
}


all_one_letter_points = {
	"a": 1,
	"b": 1,
	"c": 1,
	"d": 1,
	"e": 1,
	"f": 1,
	"g": 1,
	"h": 1,
	"i": 1,
	"j": 1,
	"k": 1,
	"l": 1,
	"m": 1,
	"n": 1,
	"o": 1,
	"p": 1,
	"q": 1,
	"r": 1,
	"s": 1,
	"t": 1,
	"u": 1,
	"v": 1,
	"w": 1,
	"x": 1,
	"y": 1,
	"z": 1,
	"*": 0
}

SCRABBLE_LETTER_POINTS = {
	"a": 1 , "b": 3 , "c": 3 , "d": 2 ,
    "e": 1 , "f": 4 , "g": 2 , "h": 4 ,
    "i": 1 , "j": 8 , "k": 5 , "l": 1 ,
    "m": 3 , "n": 1 , "o": 1 , "p": 3 ,
    "q": 10, "r": 1 , "s": 1 , "t": 1 ,
    "u": 1 , "v": 4 , "w": 4 , "x": 8 ,
    "y": 4 , "z": 10, "*": 0
}