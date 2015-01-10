import itertools
import functools
class CommonEqualityMixin(object):
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		else:
			return False
	def __ne__(self, other):
		return not self.__eq__(other)
	def __hash__(self):
		return hash(self.__str__())
class BareNote(CommonEqualityMixin):
	@staticmethod
	def extract_letter(s):
		return s[0]
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
		return BareNote.extract_letter(self.name)
	def accidental(self):
		return BareNote.extract_accidental(self.name)
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.__str__()

@functools.total_ordering
class Note(BareNote):
	@staticmethod
	def extract_octave(s):
		return int(s[-1]) #always last
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
	def __lt__ (self, other):
		return self.num() < other.num()
Keys = {
	"Cb":[BareNote('Cb'),BareNote('Db'),BareNote('Eb'),BareNote('Fb'),BareNote('Gb'),BareNote('Ab'),BareNote('Bb')],
	"C":[BareNote('C'),BareNote('D'),BareNote('E'),BareNote('F'),BareNote('G'),BareNote('A'),BareNote('B')],
	"C#":[BareNote('C#'),BareNote('D#'),BareNote('E#'),BareNote('F#'),BareNote('G#'),BareNote('A#'),BareNote('B#')],
	"Db":[BareNote('Db'),BareNote('Eb'),BareNote('F'),BareNote('Gb'),BareNote('Ab'),BareNote('Bb'),BareNote('C')],
	"D":[BareNote('D'),BareNote('E'),BareNote('F#'),BareNote('G'),BareNote('A'),BareNote('B'),BareNote('C#')],
	"D#":[BareNote('D#'),BareNote('E#'),BareNote('F##'),BareNote('G#'),BareNote('A#'),BareNote('B#'),BareNote('C##')],
	"Eb":[BareNote('Eb'),BareNote('F'),BareNote('G'),BareNote('Ab'),BareNote('Bb'),BareNote('C'),BareNote('D')],
	"E":[BareNote('E'),BareNote('F#'),BareNote('G#'),BareNote('A'),BareNote('B'),BareNote('C#'),BareNote('D#')],
	"E#":[BareNote('E#'),BareNote('F##'),BareNote('G##'),BareNote('A#'),BareNote('B#'),BareNote('C##'),BareNote('D##')],
	"Fb":[BareNote('Fb'),BareNote('Gb'),BareNote('Ab'),BareNote('Bbb'),BareNote('Cb'),BareNote('Db'),BareNote('Eb')],
	"F":[BareNote('F'),BareNote('G'),BareNote('A'),BareNote('Bb'),BareNote('C'),BareNote('D'),BareNote('E')],
	"F#":[BareNote('F#'),BareNote('G#'),BareNote('A#'),BareNote('B'),BareNote('C#'),BareNote('D#'),BareNote('E#')],
	"Gb":[BareNote('Gb'),BareNote('Ab'),BareNote('Bb'),BareNote('Cb'),BareNote('D'),BareNote('Eb'),BareNote('F')],
	"G":[BareNote('G'),BareNote('A'),BareNote('B'),BareNote('C'),BareNote('D'),BareNote('E'),BareNote('F#')],
	"G#":[BareNote('G#'),BareNote('A#'),BareNote('B#'),BareNote('C#'),BareNote('D#'),BareNote('E#'),BareNote('F##')],
	"Ab":[BareNote('Ab'),BareNote('Bb'),BareNote('C'),BareNote('Db'),BareNote('Eb'),BareNote('F'),BareNote('G')],
	"A":[BareNote('A'),BareNote('B'),BareNote('C#'),BareNote('D'),BareNote('E'),BareNote('F#'),BareNote('G#')],
	"A#":[BareNote('A#'),BareNote('B#'),BareNote('C##'),BareNote('D#'),BareNote('E#'),BareNote('F##'),BareNote('G##')],
	"Bb":[BareNote('Bb'),BareNote('C'),BareNote('D'),BareNote('Eb'),BareNote('F'),BareNote('G'),BareNote('A')],
	"B":[BareNote('B'),BareNote('C#'),BareNote('D#'),BareNote('E'),BareNote('F#'),BareNote('G#'),BareNote('A#')],
	"B#":[BareNote('B#'),BareNote('C##'),BareNote('D##'),BareNote('E#'),BareNote('F##'),BareNote('G##'),BareNote('A##')],
	#TODO: Add minor keys
}
class Triad(CommonEqualityMixin):
	def root(self):
		return Keys[self.name][0]
	def third(self):
		return Keys[self.name][2]
	def fifth(self):
		return Keys[self.name][4]
	def notes(self):
		return [self.root(),self.third(),self.fifth()]
	def __init__(self,name): #name is like Gm, g, C, CM, e, Em (both forms of minor accepted)
		if "m" in name:
			name = name[1:].lower()
		name.replace("M","")
		self.name = name
		self.note_name = name[0].upper()+name[1:]
Ranges = {
	"bass":[Note("G2"),Note("C4")],
	"tenor":[Note("C3"),Note("G4")],
	"alto": [Note("G3"),Note("C5")],
	"soprano": [Note("C4"),Note("G5")]
}
Voices = {
	"bass":0,
	"tenor":1,
	"alto":2,
	"soprano":3,
	0:"bass",
	1:"tenor",
	2:"alto",
	3:"soprano"
}
def findall(tr, double=0): #note range, triad, given notes (as array of bare notes)
	low = Ranges["bass"][0]
	high = Ranges["soprano"][1]
	def loop(low, high, note):
		initial_octave = low.octave()
		max_octave = high.octave()
		res = []
		for x in range(initial_octave, max_octave+1):
			tmp = Note.from_bare_note(note,x)
			if tmp.num() >= low.num() and tmp.num() <= high.num():
				res.append(tmp)
		return res
	param = tr.notes()
	if double == 0:
		param.append(tr.root())
	elif double == 1:
		param.append(tr.third())
	elif double == 2:
		param.append(tr.fifth())
	results = []
	for val in param:
		arr = loop(low, high, val)
		results.append(arr)
	data = [sorted(set(val)) for val in itertools.product(*results)]
	return  [val for val in data if len(val) == 4 and val[0] >= Ranges["bass"][0] and val[0] <= Ranges["bass"][1] and val[1] >= Ranges["tenor"][0] and val[1] <= Ranges["tenor"][1] and val[2] >= Ranges["alto"][0] and val[0] <= Ranges["alto"][1] and val[3] >= Ranges["soprano"][0] and val[0] <= Ranges["soprano"][1]]



def main():
	print(findall(Triad("G")))
if __name__ == "__main__":
	main()