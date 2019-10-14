# !/usr/bin/python3
# By Sam Slate, 2019. Released to the public domain.
#
# Based on A.W. Appel, G.J. Jacobson, The world's fastest Scrabble program Comm. ACM, 31 (5) (1988), pp. 572-578
#
# Uses dawg implementation by Steve Hanov at http://stevehanov.ca/blog/?id=115

from dawg import *

# Class to define a square on the baord
class Square:
	def __init__(self, tile, bonus):
		self.tile = tile
		self.bonus = bonus
		self.v_cross_checks = set()
		self.h_cross_checks = set()
		self.v_cross_score = 0
		self.h_cross_score = 0

	def switch_cross_checks(self):
		self.h_cross_checks, self.v_cross_checks = self.v_cross_checks, self.h_cross_checks

	def switch_cross_scores(self):
		self.h_cross_score, self.v_cross_score = self.v_cross_score, self.h_cross_score

# Class to define a single move
class Move:
	def __init__(self):
		self.letters = []
		self.score = 0
		self.direction = None
		self.start_coords = None

	def print(self):
		string = "".join([ML.letter for ML in self.letters])
		print("{}: {} points. {} starting at {}".format(string, self.score, self.direction, self.start_coords))

	def serialize(self):
		return "".join([ML.letter for ML in self.letters])

# Class to define a letter in a single move
class MoveLetter:
	def __init__(self, letter, already_placed, was_blank=False):
		self.letter = letter
		self.already_placed = already_placed
		self.was_blank = was_blank

# Class to define a dictionary
class Dictionary(object):
	def __init__(self, dictionary_file):
		self.dawg = Dawg()
		self.import_dictionary(dictionary_file)

	def import_dictionary(self, dictionary_file):

		WordCount = 0
		words = open(dictionary_file, "rt").read().split()
		words.sort()
		start = time.time()    
		for word in words:
		    WordCount += 1
		    # insert all words, using the reversed version as the data associated with
		    # it
		    self.dawg.insert(word, ''.join(reversed(word)))
		    if ( WordCount % 100 ) == 0: print("{0}\r".format(WordCount), end="")
		self.dawg.finish()
		print("Dawg creation took {0} s".format(time.time()-start))

	def get_root(self):
		return self.dawg.root

	def check_word(self, word):
		return self.dawg.lookup(word)

	def attempt_trace_prefix(self, prefix):
		cur_node = self.dawg.root
		for char in prefix:
			# Check if the prefix so far is the start of any word
			if char not in cur_node.edges.keys():
				# If not, return False to say that the prefix does not start any words
				return False
			else:
				# Othwise, continue following the prefix
				cur_node = cur_node.edges[char]

		# At the very end, we return the node at the end of the prefix
		return cur_node