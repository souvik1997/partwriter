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
	pitches = {"Cbbb":-3,"Cbb":-2,"Cb":-1,"C":0,"C#":1,"C##":2,"C###":3,
				"Dbbb":-1,"Dbb":0,"Db":1,"D":2,"D#":3,"D##":4,"D###":5,
				"Ebbb":1,"Ebb":2,"Eb":3,"E":4,"E#":5,"E##":6,"E###":7,
				"Fbbb":2,"Fbb":3,"Fb":4,"F":5,"F#":6,"F##":7,"F###":8,
				"Gbbb":4,"Gbb":5,"Gb":6,"G":7,"G#":8,"G##":9,"G###":10,
				"Abbb":6,"Abb":7,"Ab":8,"A":9,"A#":10,"A##":11,"A###":12,
				"Bbbb":8,"Bbb":9,"Bb":10,"B":11,"B#":12,"B##":13,"B###":14}
	def ascending_interval(self,invl):
		def search(s):
			res = []
			for k,v in BareNote.pitches.items():
				if v == s:
					res.append(k)
			return res
		invls = {
			"P1":0,
			"d2":0,
			"m2":1,
			"M2":2,
			"A2":3,
			"d3":2,
			"m3":3,
			"M3":4,
			"A3":5,
			"d4":4,
			"P4":5,
			"A4":6,
			"d5":6,
			"P5":7,
			"A5":8,
			"d6":7,
			"m6":8,
			"M6":9,
			"A6":10,
			"d7":11,
			"m7":10,
			"M7":11,
			"A7":12,
			"P8":12,
		}
		carry = False
		if invl == "P8":
			return (Note(self.name),1)
		elif invl == "P1":
			return (Note(self.name),0)
		target = self.up_letter(int(invl[-1])-1)
		if "CDEFGAB".index(self.letter())+int(invl[-1]) > 7:
			carry = True
		new_pitch = (self.pitch() + invls[invl]) % 12 if carry else (self.pitch() + invls[invl])
		#print(self.pitch(),invls[invl],new_pitch)
		return (BareNote([val for val in search(new_pitch) if val.find(target) > -1][0]), 1 if carry else 0)
	def pitch(self):
		return BareNote.pitches[self.letter()+self.accidental()]
	def up_letter(self, amnt):
		seq = "CDEFGABCDEFGAB"
		return seq[seq.index(self.letter())+int(amnt)]
	def __init__(self,name):
		self.name = name
	def letter(self):
		return self.name[0]
	def accidental(self):
		ac = self.name[1:]
		if ac not in ["##","#","b","bb"]:
			return ""
		return ac
	def __str__(self):
		return self.name
	def __repr__(self):
		return self.__str__()
@functools.total_ordering
class Note(BareNote):
	@staticmethod
	def from_bare_note(bn, octave):
		return Note(bn.name+str(octave))
	def ascending_interval(self,invl):
		res,carry=super().ascending_interval(invl)
		res = Note.from_bare_note(res,self.octave())
		if carry == 1:
			return res.up_octave()
		return res
	def octave(self):
		return int(self.name[-1])
	def up_octave(self):
		return Note(self.letter()+self.accidental()+str(self.octave()+1))
	def down_octave(self):
		return Note(self.letter()+self.accidental()+(self.octave()-1))
	def num(self):
		return self.pitch()+12*self.octave()
	def bare_name(self):
		return self.letter()+self.accidental()
	def __lt__ (self, other):
		return self.num() < other.num()

class Triad(CommonEqualityMixin):
	def note(self,pos):
		return self.root.ascending_interval(Triad.types[self.type][pos])[0]
	def notes(self):
		ns = []
		for x in range(0,len(Triad.types[self.type])):
			ns.append(self.note(x))
		return ns
	types = {
		"M": ["P1","M3","P5"],
		"m": ["P1","m3","P5"],
		"M7": ["P1", "M3","P5","M7"],
		"m7": ["P1", "m3", "P5","m7"],
		"mM7": ["P1", "m3", "P5", "M7"],
		"7": ["P1", "M3", "P5", "m7"],
		"dim": ["P1", "m3", "d5"],
		"dim7": ["P1", "m3", "d5", "d7"],
		"halfdim7": ["P1", "m3", "d5", "m7"],
		"aug": ["P1","M3","A5"]
	}
	def __init__(self,root,type): #name is like Gm, g, C, CM, e, Em (both forms of minor accepted)
		self.type = type
		self.root = root
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
	if double >= 0:
		param.append(tr.notes()[double])
	results = []
	for val in param:
		arr = loop(low, high, val)
		results.append(arr)
	data = [sorted(set(val)) for val in itertools.product(*results)]
	return  [val for val in data if len(val) == 4 and val[0] >= Ranges["bass"][0] and val[0] <= Ranges["bass"][1] and val[1] >= Ranges["tenor"][0] and val[1] <= Ranges["tenor"][1] and val[2] >= Ranges["alto"][0] and val[0] <= Ranges["alto"][1] and val[3] >= Ranges["soprano"][0] and val[0] <= Ranges["soprano"][1]]
def main():
	print(findall(Triad(BareNote("C"),"7"),double=-1))
if __name__ == "__main__":
	main()