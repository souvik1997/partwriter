import itertools
class CommonEqualityMixin(object):
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		else:
			return False
	def __ne__(self, other):
		return not self.__eq__(other)
class BareNote(CommonEqualityMixin):
	@staticmethod
	def extract_letter(s):
		return s[0]
	@staticmethod
	def extract_octave(s):
		return int(s[-1]) #always last
	@staticmethod
	def extract_accidental(s):
		return s[:-1][1:]
	@staticmethod
	def next_letter(s):
		seq = "CDEFGABC"
		return seq[seq.index(extract_letter(s))+1]
	@staticmethod
	def previous_letter(s):
		seq = "CDEFGAB"
		letter =  extract_letter(s)
		if letter == "C":
			return "B"
		else:
			return seq[seq.index(letter)-1]
	def __init__(self,name):
		self.name = name
	def letter(self):
		return Note.extract_letter(self.name)
	def accidental(self):
		return Note.extract_accidental(self.name)
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.__str__()
class Note(BareNote):
	@staticmethod
	def convert_name_to_number(name): #name is like "A4", "C#1", "D2", etc.
		names = {"Cbb":-2,"Cb":-1,"C":0,"C#":1,"C##":2,
				"Dbb":0,"Db":1,"D":2,"D#":3,"D##":4,
				"Ebb":2,"Eb":3,"E":4,"E#":5,"E##":6,
				"Fbb":3,"Fb":4,"F":5,"F#":6,"F##":7,
				"Gbb":5,"Gb":6,"G":7,"G#":8,"G##":9,
				"Abb":7,"Ab":8,"A":9,"A#":10,"A##":11,
				"Bbb":9,"Bb":10,"B":11,"B#":12,"B##":13}
		return names[Note.extract_letter(name)+Note.extract_accidental(name)]+12*Note.extract_octave(name)
	@staticmethod
	def from_bare_note(bn, octave):
		return Note(bn.name+str(octave))
	def octave(self):
		return Note.extract_octave(self.name)
	def up_octave(self):
		return Note(self.letter()+self.accidental()+(self.octave()+1))
	def down_octave(self):
		return Note(self.letter()+self.accidental()+(self.octave()-1))
	def num(self):
		return Note.convert_name_to_number(self.name)
	def bare_name(self):
		return self.letter()+self.accidental()
Triads = {
		"C":[BareNote('C'),BareNote('E'),BareNote('G')],
		"C#":[BareNote('C#'),BareNote('E#'),BareNote('G#')],
		"Db":[BareNote('Db'),BareNote('F'),BareNote('Ab')],
		"D":[BareNote('D'),BareNote('F#'),BareNote('A')],
		"D#":[BareNote('D#'),BareNote('F##'),BareNote('A#')],
		"Eb":[BareNote('Eb'),BareNote('G'),BareNote('Bb')],
		"E":[BareNote('E'),BareNote('G#'),BareNote('B')],
		"F":[BareNote('F'),BareNote('A'),BareNote('C')],
		"F#":[BareNote('F#'),BareNote('A#'),BareNote('C#')],
		"Gb":[BareNote('Gb'),BareNote('Bb'),BareNote('Db')],
		"G":[BareNote('G'),BareNote('B'),BareNote('D')],
		"G#":[BareNote('G#'),BareNote('B#'),BareNote('D#')],
		"Ab":[BareNote('Ab'),BareNote('C'),BareNote('Eb')],
		"A":[BareNote('A'),BareNote('C#'),BareNote('E')],
		"A#":[BareNote('A#'),BareNote('C##'),BareNote('E#')],
		"Bb":[BareNote('Bb'),BareNote('D'),BareNote('F')],
		"B":[BareNote('B'),BareNote('D#'),BareNote('F#')],
		"c":[BareNote('C'),BareNote('Eb'),BareNote('G')],
		"c#":[BareNote('C#'),BareNote('E'),BareNote('G')],
		"db":[BareNote('Db'),BareNote('Fb'),BareNote('Ab')],
		"d":[BareNote('D'),BareNote('F'),BareNote('A')],
		"d#":[BareNote('D#'),BareNote('F#'),BareNote('A#')],
		"eb":[BareNote('Eb'),BareNote('G'),BareNote('Bb')],
		"e":[BareNote('E'),BareNote('G'),BareNote('B')],
		"f":[BareNote('F'),BareNote('Ab'),BareNote('C')],
		"f#":[BareNote('F#'),BareNote('A'),BareNote('C#')],
		"gb":[BareNote('Gb'),BareNote('Bbb'),BareNote('Db')],
		"g":[BareNote('G'),BareNote('Bb'),BareNote('D')],
		"g#":[BareNote('G#'),BareNote('B'),BareNote('D#')],
		"ab":[BareNote('Ab'),BareNote('Cb'),BareNote('Eb')],
		"a":[BareNote('A'),BareNote('C'),BareNote('E')],
		"a#":[BareNote('A#'),BareNote('C#'),BareNote('E#')],
		"bb":[BareNote('Bb'),BareNote('Db'),BareNote('F#')],
		"b":[BareNote('B'),BareNote('D'),BareNote('F#')],
	}
class Triad:
	def root(self):
		return Triads[self.name][0]
	def third(self):
		return Triads[self.name][1]
	def fifth(self):
		return Triads[self.name][2]
	def notes(self):
		return Triads[self.name]
	def __init__(self,name): #name is like Gm, g, C, CM, e, Em (both forms of minor accepted)
		if "m" in name:
			name = name[1:].lower()
		name.replace("M","")
		self.name = name
		self.note_name = name[0].upper()+name[1:]
def findall(low, high, tr, given=[]): #note range, triad, given notes (as array of bare notes)
	def loop(low, high, note):
		initial_octave = low.octave()
		max_octave = high.octave()
		res = []
		for x in range(initial_octave, max_octave+1):
			tmp = Note.from_bare_note(note,x)
			if tmp.num() >= low.num() and tmp.num() <= high.num():
				res.append(tmp)
		return res
	notgiven = []
	for n in tr.notes():
		if n not in given:
			notgiven.append(n)
	results = []
	for val in notgiven:
		arr = loop(low, high, val)
		results.append(arr)
	return itertools.product(*results)