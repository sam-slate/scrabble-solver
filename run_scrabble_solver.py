# !/usr/bin/python3
# By Sam Slate, 2019. Released to the public domain.
#
# Based on A.W. Appel, G.J. Jacobson, The world's fastest Scrabble program Comm. ACM, 31 (5) (1988), pp. 572-578
#
# Uses dawg implementation by Steve Hanov at http://stevehanov.ca/blog/?id=115

import scrabble_solver_game_without_debug
from helper_lists import SCRABBLE_HEIGHT, SCRABBLE_WIDTH, DOUBLE_LETTER, TRIPLE_LETTER, DOUBLE_WORD, TRIPLE_WORD, BLANK, SCRABBLE_BINGO_BONUS, SCRABBLE_BONUS_PLACEMENTS, SCRABBLE_LETTER_POINTS, DICTIONARY

placed_tiles_1 = {
	(4, 7): "a",
	(5, 7): "f",
	(6, 7): "t",
	(7, 7): "e",
	(8, 7): "r",
	(8, 5): "h",
	(8, 6): "a",
	(8, 8): "d"
}

current_rack_1 = ["a", "v", "e", "r", "f", "u", "m"]


if __name__ == "__main__":
	game = scrabble_solver_game_without_debug.Game(SCRABBLE_HEIGHT, SCRABBLE_WIDTH, placed_tiles_1, SCRABBLE_BONUS_PLACEMENTS, SCRABBLE_LETTER_POINTS, current_rack_1, SCRABBLE_BINGO_BONUS, DICTIONARY)
	game.Algorithm()
	game.print_possible_words()
	game.print_highest()
	game.print()