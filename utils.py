import torch
import num2words
import re

class TextProcess:
	def __init__(self):
		char_map_str = """
		' 0
		<SPACE> 1
		a 2
		b 3
		c 4
		d 5
		e 6
		f 7
		g 8
		h 9
		i 10
		j 11
		k 12
		l 13
		m 14
		n 15
		o 16
		p 17
		q 18
		r 19
		s 20
		t 21
		u 22
		v 23
		w 24
		x 25
		y 26
		z 27
		"""
		self.char_map = {}
		self.index_map = {}
		for line in char_map_str.strip().split('\n'):
			ch, index = line.split()
			self.char_map[ch] = int(index)
			self.index_map[int(index)] = ch
		self.index_map[1] = ' '

	def text_to_int_sequence(self, text):
		""" Use a character map and convert text to an integer sequence """
		int_sequence = []
		for c in text:
			if c == ' ':
				ch = self.char_map['<SPACE>']
			else:
				ch = self.char_map[c]
			int_sequence.append(ch)
		return int_sequence

	def int_to_text_sequence(self, labels):
		""" Use a character map and convert integer labels to an text sequence """
		string = []
		for i in labels:
			string.append(self.index_map[i])
		return ''.join(string).replace('<SPACE>', ' ')

	# methods to clean text
	def clean_text(self, text):
		text = text.lower()
		text = self.remove_punctuations(text)
		text = self.convert_year_to_words(text)
		text = self.convert_num_to_words(text)
		text = text.replace('-', ' ')
		return text

	def convert_year_to_words(self, text):
	    text = ' '.join([num2words.num2words(i, to='year') if (i.isdigit() & (len(i) == 4)) else i for i in text.split()])
	    return text

	def convert_num_to_words(self, text):
	    text = ' '.join([num2words.num2words(i) if i.isdigit() else i for i in text.split()])
	    return text

	def remove_punctuations(self, text):
		text = re.sub(r'[^\w\s]', ' ', text)
		return text



	        # label = self.text_process.remove_punctuations(self.labels[index])
        # label = self.text_process.convert_year_to_words(self.labels[index])
        # label = self.text_process.convert_num_to_words(self.labels[index])
        # convert_num_to_words



# def GreedyDecoder(output, labels, label_lengths, blank_label=28, collapse_repeated=True):
# 	arg_maxes = torch.argmax(output, dim=2)
# 	decodes = []
# 	targets = []
# 	for i, args in enumerate(arg_maxes):
# 		decode = []
# 		targets.append(textprocess.int_to_text_sequence(
# 				labels[i][:label_lengths[i]].tolist()))
# 		for j, index in enumerate(args):
# 			if index != blank_label:
# 				if collapse_repeated and j != 0 and index == args[j -1]:
# 					continue
# 				decode.append(index.item())
# 		decodes.append(textprocess.int_to_text_sequence(decode))
# 	return decodes, targets