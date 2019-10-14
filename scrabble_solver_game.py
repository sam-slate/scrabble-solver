# !/usr/bin/python3
# By Sam Slate, 2019. Released to the public domain.
#
# Based on A.W. Appel, G.J. Jacobson, The world's fastest Scrabble program Comm. ACM, 31 (5) (1988), pp. 572-578
#
# Uses dawg implementation by Steve Hanov at http://stevehanov.ca/blog/?id=115

from helper_lists import *
from collections import namedtuple
from string import ascii_lowercase
from copy import deepcopy

from solver_helper_classes import Square, Move, MoveLetter, Dictionary

DOUBLE_LETTER = "dl"
TRIPLE_LETTER = "tl"
DOUBLE_WORD = "dw"
TRIPLE_WORD = "tw"

# Class to define a scrabble game
class Game:

	def __init__(self, height, width, placed_tiles, bonus_placements, letter_points, current_rack, bingo_bonus, dictionary_file, debug=False):
		self.dictionary = Dictionary(dictionary_file)
		self.debug = debug

		self.letter_points = letter_points
		self.bingo_bonus = bingo_bonus
		self.board_is_blank = len(placed_tiles) == 0

		# Board is indexed [x, y] starting from [0, 0] in the top left corner
		self.create_board(height, width, placed_tiles, bonus_placements)
		self.height = height
		self.width = width

		# Variable to keep track of whether or not the board is transposed
		self.transposed = False 

		self.possible_moves = []

		# Evaluate both horizontal and vertical cross checks and cross scores
		self.print_debug_statement("Calculating horizontal cross checks and scores")
		self.eval_cross_checks_and_scores()
		self.transpose()
		self.print_debug_statement("Calculating vertical cross checks and scores")
		self.eval_cross_checks_and_scores()
		self.transpose()

		self.current_rack = current_rack
		self.bonus_placements = bonus_placements

	def create_board(self, height, width, placed_tiles, bonus_placements):
		self.board = []
		for i in range(width):
			self.board.append([])
			for j in range(height):
				# Initialize a new square with blank information
				new_square = Square(None, None)
				self.board[i].append(new_square)

		self.insert_tiles(placed_tiles)
		self.insert_bonuses(bonus_placements)

	def insert_tiles(self, tiles):
		for coords, tile in tiles.items():
			self.board[coords[0]][coords[1]].tile = tile

	def insert_bonuses(self, bonuses):
		self.print_debug_statement("inserting bonuses")
		for coords, bonus in bonuses.items():
			self.print_debug_statement("Coords are {}, {} and bonus is: {}".format(coords[0], coords[1], bonus))
			self.board[coords[0]][coords[1]].bonus = bonus

	def eval_cross_checks_and_scores(self):
		for i in range(self.width):
			for j in range(self.height):
				self.print_debug_statement("Calculating cross checks for {},{}".format(i, j))
				if self.board[i][j].tile:
					continue

				# Initialize strings to hold left and right sides	
				left, right = "", ""
				left_index, right_index = i - 1, i + 1

				# Loops to either side, adding tiles to the strings and their point value to
				# the cross score.
				while (left_index >= 0 and self.board[left_index][j].tile):
					left = self.board[left_index][j].tile + left
					self.board[i][j].h_cross_score += self.letter_points[self.board[left_index][j].tile]
					left_index -= 1

				while (right_index < self.width and self.board[right_index][j].tile):
					right = right + self.board[right_index][j].tile
					self.board[i][j].h_cross_score += self.letter_points[self.board[right_index][j].tile]
					right_index += 1 

				self.print_debug_statement("Left: {}".format(left))
				self.print_debug_statement("Right: {}".format(right))

				# If there is neither a left nor right, add all letters
				if not left and not right:
					self.board[i][j].h_cross_checks = set(ascii_lowercase)
				else:
					# Check if each letter can be placed in the spot
					for letter in ascii_lowercase:
						potential_word = left + letter + right
						if self.dictionary.check_word(potential_word):
							self.print_debug_statement("{} is a potential word!".format(potential_word))
							self.board[i][j].h_cross_checks.add(letter)

				# If there are any letters in the cross check, we can add the blank
				if len(self.board[i][j].h_cross_checks) > 0:
					self.board[i][j].h_cross_checks.add("*")

				self.print_debug_statement(len(self.board[i][j].h_cross_checks))

				self.print_debug_statement("Cross checks are: {}".format(', '.join(self.board[i][j].h_cross_checks)))
				self.print_debug_statement("Cross score is: {}".format(self.board[i][j].h_cross_score))

	def transpose(self):
		# Transposes the board itself
		self.board = [*zip(*self.board)]

		# Switch height and width
		self.height, self.width = self.width, self.height

		# Switch the horizontal and vertical cross checks and scores
		for i in range(self.width):
			for j in range(self.height):
				self.board[i][j].switch_cross_checks()
				self.board[i][j].switch_cross_scores()

		# Update tranpose variable
		self.transposed = not self.transposed

	def print(self):
		print("          " + "    ".join(map(str, range(self.width))))
		for j in range(self.height):
			hor_string = str(j) + "\t"
			for i in range(self.width):
				tile = self.board[i][j].tile
				if not tile:
					bonus = self.board[i][j].bonus
					if bonus:
						tile = "~" + bonus
					else:
						tile = "   "
				else:
					tile = " " + tile + " "
				hor_string += "|" + tile + "|"
			print(hor_string + " " + str(j))
		print("          " + "    ".join(map(str, range(self.width))))

	def print_elaborate(self):
		print("printing elaborate")
		for j in range(self.height):
			for i in range(self.width):
				hor_string = ""
				tile = self.board[i][j].tile
				if not tile:
					tile = " "
				hor_string += str(i) + ", " + str(j) + " " + tile + " "
				if self.board[i][j].bonus:
					hor_string += self.board[i][j].bonus + " "
				hor_string += "H cross checks: {} ".format(', '.join(self.board[i][j].h_cross_checks)) + " "
				hor_string += "V cross checks: {}".format(', '.join(self.board[i][j].v_cross_checks)) + " "
				hor_string += "H cross score: {}".format(self.board[i][j].h_cross_score) + " "
				hor_string += "V cross score: {}".format(self.board[i][j].v_cross_score)
				print(hor_string)

	def get_anchors(self, row_index):
		anchors = []

		# Loops through a row
		for i in range(self.width):
			# If tile, not an anchor
			if self.board[i][row_index].tile:
				continue
			is_anchor = False
			# Make sure not at the left edge
			if i > 0:
				if self.board[i-1][row_index].tile:
					is_anchor = True
			# Make sure not at the right edge
			if i < self.width - 1:
				if self.board[i+1][row_index].tile:
					is_anchor = True
			# Make sure not at the top row
			if row_index > 0:
				if self.board[i][row_index-1].tile:
					is_anchor = True
			# Make sure not at the bottom row
			if row_index < self.height - 1:
				if self.board[i][row_index+1].tile:
					is_anchor = True

			if is_anchor:
				anchors.append((i, row_index))

		return anchors

	def Algorithm(self):
		# Call the horizontal version of the algorithm, tranpose, call the algorithm again, then transpose back
		self.AlgorithmHorizontal()
		self.transpose()
		self.AlgorithmHorizontal()
		self.transpose()

	def AlgorithmHorizontal(self):
		# Check if empty board
		if self.board_is_blank:
			x, y = int(self.width/2), int(self.height/2)

			# Calculate the limit as whichever is the shortest, the size of the rack or distance from edge
			if x < len(self.current_rack) - 1:
				limit = x
			else:
				limit = len(self.current_rack) - 1

			self.LeftPart("", self.dictionary.get_root(), limit, (x, y), Move())

			return 

		# Loop through rows
		for j in range(self.height):
			# Get anchors to use in the algorithm
			anchors = self.get_anchors(j)

			# Set previous anchor value to the left edge - 1 (seems to work)
			previous_anchor_x_value = -1
			
			# Loop through anchors
			for anchor in anchors:
				# Check if anchor is directly to the right of a tile. If so, call ExtendRight directly
				if anchor[0] > 0:
					if self.board[anchor[0] - 1][j].tile:
						move = Move()

						# If so, get the prefix directly
						prefix = ""
						left_index = anchor[0] - 1
						while (left_index >= 0 and self.board[left_index][j].tile):
							prefix = self.board[left_index][j].tile + prefix

							# Prepend letter to Move indicating that it is already a tile
							move.letters.insert(0, MoveLetter(self.board[left_index][j].tile, True))

							left_index -= 1

						self.print_debug_statement("Anchor is {} and is to the right of a tile, with a prefix of {}".format(anchor, prefix))

						# Get the node at the end of the prefix if it exists
						prefix_node = self.dictionary.attempt_trace_prefix(prefix)

						# Check if the prefix starts a word
						if prefix_node:
							self.print_debug_statement("The prefix starts a word!")
							self.ExtendRight(prefix, prefix_node, anchor, move)
						else:
							self.print_debug_statement("The prefix does not start a word")

						# Update previous anchor x value
						previous_anchor_x_value = anchor[0]
						continue

				# This means there is an empty tile to the left of the anchor

				dist_from_last_anchor = anchor[0] - previous_anchor_x_value -1
				# Calculate the limit as whichever is the shortest, the size of the rack or distance from
				# 	last anchor
				if dist_from_last_anchor < len(self.current_rack) - 1:
					limit = dist_from_last_anchor
				else:
					limit = len(self.current_rack) - 1
				self.print_debug_statement("Anchor is {} with limit of {}".format(anchor, limit))

				self.print_debug_statement("The partial words are:")
				self.LeftPart("", self.dictionary.get_root(), limit, anchor, Move())
				# Update previous anchor x value
				previous_anchor_x_value = anchor[0]

	def LeftPart(self, PartialWord, cur_node, limit, anchor, move):
		self.print_debug_statement(PartialWord)
		self.ExtendRight(PartialWord, cur_node, anchor, deepcopy(move))
		if limit > 0:
			for letter, next_node in cur_node.edges.items():
				# Check if the letter is in the current rack 
				if letter in self.current_rack:
					self.current_rack.remove(letter)
					# Add letter to move and indicate that it was not already a tile
					move.letters.append(MoveLetter(letter, False))
					self.LeftPart(PartialWord + letter, next_node, limit-1, anchor, deepcopy(move))
					self.current_rack.append(letter)
					# Remove letter from move
					move.letters.pop()

				# Check if there is a blank in the current rack
				#     - The reason why this is another if statement is that we want both cases
				#		when we could use a letter or a blank, in order to account for various
				#		scores
				if BLANK in self.current_rack:
					self.current_rack.remove(BLANK)
					# Add letter to move and indicate that it was not already a tile and was a blank
					move.letters.append(MoveLetter(letter, False, True))
					self.LeftPart(PartialWord + letter, next_node, limit-1, anchor, deepcopy(move))
					self.current_rack.append(BLANK)
					# Remove letter from move
					move.letters.pop()


	def ExtendRight(self, PartialWord, cur_node, coords, move):
		self.print_debug_statement("Current partial word is: {} at {}".format(PartialWord, coords))
		self.print_debug_statement("Current rack is: {}".format(self.current_rack))

		x, y = coords[0], coords[1]

		# Check if we have reached the edge. If so, return
		if x >= self.width:
			self.print_debug_statement("\tReached the edge!")
			return

		# Check if we have landed on a tile
		if not self.board[x][y].tile:
			self.print_debug_statement("\tNot a tile!")
			self.print_debug_statement("\tChecking each letter")
			# Check each possible letter to continue the word
			for letter, next_node in cur_node.edges.items():
				self.print_debug_statement("\tChecking: {}".format(letter))
				# Check if possible letter is in our rack
				if letter in self.current_rack: 
					self.print_debug_statement("\t\t{} is in the rack".format(letter))
					# Check if possible letter fits vertically
					if letter in self.board[x][y].v_cross_checks:
						self.print_debug_statement("\t\t{} is in vertical cross checks.".format(letter))
						# Add letter to move and indicate that it was not already a tile
						move.letters.append(MoveLetter(letter, False))

						# Check if we have reached a compelete word in the dictionary
						if next_node.final:
							# Check if either the tile to the right is empty or we hit the edge
							if (x < self.width - 1 and not self.board[x + 1][y].tile) or x == self.width - 1:
								self.print_debug_statement("\t\tThe next node is final, meaning our partial word is a word")
								# We have a legal move! Call legal move with a deepcopy of the move
								self.LegalMove(PartialWord + letter, coords, deepcopy(move))

						# Take the letter off the rack, recursively call ExtendRight with the added letter,
						# and then add the letter back to the rack for continued testing
						self.current_rack.remove(letter)
						self.ExtendRight(PartialWord + letter, next_node, (x + 1, y), deepcopy(move))
						self.current_rack.append(letter)

						# Remove letter from move for continued testing
						move.letters.pop()
					else:
						self.print_debug_statement("\t\t{} is not in vertical cross checks".format(letter))
				else:
					self.print_debug_statement("\t\t{} is not in the rack".format(letter))

				if BLANK in self.current_rack: 
					self.print_debug_statement("There is a blank in the rack")
					# Check if possible letter fits vertically
					if letter in self.board[x][y].v_cross_checks:
						self.print_debug_statement("\t\t{} is in vertical cross checks.".format(letter))
						# Add letter to move and indicate that it was not already a tile and was a blank
						move.letters.append(MoveLetter(letter, False, True))

						# Check if we have reached a compelete word in the dictionary
						if next_node.final:
							# Check if either the tile to the right is empty or we hit the edge
							if (x < self.width - 1 and not self.board[x + 1][y].tile) or x == self.width - 1:
								self.print_debug_statement("\t\tThe next node is final, meaning our partial word is a word")
								# We have a legal move! Call legal move with a deepcopy of the move
								self.LegalMove(PartialWord + letter, coords, deepcopy(move))

						# Take the letter off the rack, recursively call ExtendRight with the added letter,
						# and then add the letter back to the rack for continued testing
						self.current_rack.remove(BLANK)
						self.ExtendRight(PartialWord + letter, next_node, (x + 1, y), deepcopy(move))
						self.current_rack.append(BLANK)

						# Remove letter from move for continued testing
						move.letters.pop()
					else:
						self.print_debug_statement("\t\t{} is not in vertical cross checks".format(letter))
				else:
					self.print_debug_statement("There is no blank in the rack".format(letter))
		else:
			self.print_debug_statement("\tIs the tile of: {}".format(self.board[x][y].tile))
			# If we have landed on a tile, check if the letter can be used in a word
			cur_tile = self.board[x][y].tile
			if cur_tile in cur_node.edges.keys():
				# Add letter to move and indicate that it was a tile
				move.letters.append(MoveLetter(cur_tile, True))

				self.print_debug_statement("\t\tAdded tile makes a prefix.")
				# Check if we have reached a compelete word in the dictionary
				if cur_node.edges[cur_tile].final:
					# Check if either the tile to the right is empty or we hit the edge
					if (x < self.width - 1 and not self.board[x + 1][y].tile) or x == self.width - 1:
						self.print_debug_statement("\t\tThe next node is final, meaning our partial word is a word")
					    # We have a legal move! Call legal move with a deepcopy of the move
						self.LegalMove(PartialWord + cur_tile, coords, deepcopy(move))

				# Recursively call ExtendRight with the added letter
				self.ExtendRight(PartialWord + cur_tile, cur_node.edges[cur_tile], (x + 1, y), deepcopy(move))
			else:
				self.print_debug_statement("\tAdded tile does not make a prefix")

	def LegalMove(self, PartialWord, coords, move):

		coords = (coords[0] - len(PartialWord) + 1, coords[1])

		if self.transposed:
			# If transposed, switch the x and y coords
			coords = (coords[1], coords[0])

			move.direction = "downwards"
			move.start_coords = coords
			self.score_move(move)
			self.print_debug_statement("Score outside score_move: {}".format(move.score))

			self.print_debug_statement("Legal move found by placing {} with last tile right above {}".format(PartialWord, coords))

			self.possible_moves.append(move)
		else:
			move.direction = "across"
			move.start_coords = coords
			self.score_move(move)
			self.print_debug_statement("Legal move found by placing {} with last tile to the left of {}".format(PartialWord, coords))

			self.possible_moves.append(move)

	def score_move(self, move):
		self.print_debug_statement("Scoring the move: {}".format(move.serialize()))

		hor_multiplier = 1
		hor_score = 0

		if self.transposed:
			x, y = move.start_coords[1], move.start_coords[0]
		else: 
			x, y = move.start_coords[0], move.start_coords[1]

		for move_letter in move.letters:
			# Get the point value of the letter
			letter_point_value = self.letter_points[move_letter.letter]
			# If the letter was a blank, the point value is 0
			if move_letter.was_blank:
				letter_point_value = 0
			self.print_debug_statement("\tInitial letter point value of {} is: {}".format(move_letter.letter, letter_point_value))

			if not move_letter.already_placed:
				# Get the vertical score
				v_score = self.board[x][y].v_cross_score
				self.print_debug_statement("\t\tInitial v_score is: {}".format(v_score))

				# Implement bonus
				bonus = self.board[x][y].bonus
				self.print_debug_statement("\t\tBonus is: {}".format(bonus))
				if bonus == DOUBLE_LETTER:
					self.print_debug_statement("\t\tDouble letter!")
					# Double the letter point value and then add it to the vertical score if it exists
					letter_point_value *= 2
					if v_score:
						v_score += letter_point_value
				elif bonus == TRIPLE_LETTER:
					self.print_debug_statement("\t\tTriple letter!")
					# Triple the letter point value and then add it to the vertical score if it exists
					letter_point_value *= 3					
					if v_score:
						v_score += letter_point_value
				elif bonus == DOUBLE_WORD:
					self.print_debug_statement("\t\tDouble word!")
					# Double the horizontal multiplier and then, if the vertical score exists,
					# add the letter point value to it and then double it
					hor_multiplier *= 2
					if v_score:
						v_score += letter_point_value
						v_score *= 2
				elif bonus == TRIPLE_WORD:
					self.print_debug_statement("\t\tTriple word!")
					# Triple the horizontal multiplier and then, if the vertical score exists,
					# add the letter point value to it and then triple it
					hor_multiplier *= 3
					if v_score:
						v_score += letter_point_valule
						v_score *= 3
				else: 
					# If there is a vertical score, add the letter point value to it
					if v_score:
						v_score += letter_point_value

				self.print_debug_statement("\t\tFinal v_score is: {}".format(v_score))

				# Add the finished vertical score to the total move score variable
				move.score += v_score

			self.print_debug_statement("\t\tFinal letter point value: {}".format(letter_point_value))

			# Add the final letter point value to the horizontal score
			hor_score += letter_point_value

			# Increment the x value
			x += 1

		self.print_debug_statement("\tSum of vertical scores is: {}".format(move.score))
		self.print_debug_statement("\tFinal horizontal score is: {}".format(hor_score))
		self.print_debug_statement("\tFinal horizontal multiplier is: {}".format(hor_multiplier))

		# Add the horizontal score with the applied multiplier to the total move score variable
		move.score += hor_score * hor_multiplier

		# Add bingo bonus if needed
		if len([ml for ml in move.letters if not ml.already_placed]) == 7:
			move.score += self.bingo_bonus

		self.print_debug_statement("\tScore within score_move: {}".format(move.score))

	def sort_highest(self):
		self.possible_moves.sort(key=lambda possible_move: possible_move.score, reverse=True)

	def return_highest(self):
		self.sort_highest()
		
		if not self.possible_moves:
			return None

		high_score = self.possible_moves[0].score
		i = 0
		while(self.possible_moves[i].score == high_score):
			i += 1

		return self.possible_moves[:i]

	def print_highest(self):
		highest_moves = self.return_highest()

		if not highest_moves:
			print("There are no possible moves")
			return

		total_moves = len(self.possible_moves)
		if total_moves == 1:
			singular_or_plural = ""
		else:
			singular_or_plural = "s"

		if len(highest_moves) == 1:
			print("The highest scoring move out of {} possible move{} is:".format(total_moves, singular_or_plural))
			highest_moves[0].print()
		else:
			print("The highest scoring moves out of {} possible moves are:".format(total_moves))
			for move in highest_moves:
				move.print()

	def test_ExtendRight(self, PartialWord, coords):
		self.ExtendRight(PartialWord, self.dictionary.get_root(), coords, Move())

	def test_LeftPart(self, limit, coords):
		self.LeftPart("", self.dictionary.get_root(), limit, coords, Move())

	def print_debug_statement(self, text):
		if self.debug:
			print(text)

	def print_possible_words(self):
		print("{} possible moves:".format(len(self.possible_moves)))
		for possible_move in self.possible_moves:
			possible_move.print()
