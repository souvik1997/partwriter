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
	intervals = {
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
	def ascending_interval(self,invl):
		def search(s):
			res = []
			for k,v in BareNote.pitches.items():
				if v == s:
					res.append(k)
			return res
		carry = False
		if invl == "P8":
			return (Note(self.name),1)
		elif invl == "P1":
			return (Note(self.name),0)
		target = self.up_letter(int(invl[-1])-1)
		if "CDEFGAB".index(self.letter())+int(invl[-1]) > 7:
			carry = True
		new_pitch = (self.pitch() + BareNote.intervals[invl]) % 12 if carry else (self.pitch() + BareNote.intervals[invl])
		#print(self.pitch(),BareNote.intervals[invl],new_pitch)
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
	"bass":[Note("C2"),Note("C4")],
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
class Tree:
	def __init__(self, data, master=False):
		self.children = []
		self.data = data
		self.master = master
		self.parent = None
		self.index = 0
		self.points = 0
		self.depth = 0
		self.badness = 0
	def add(self,data):
		tr = Tree(data)
		tr.depth = self.depth + 1
		tr.index = self.index + 1
		tr.parent = self
		tr.badness = self.badness
		self.children.append(tr)
		return tr
def findall(tr, double=0, norepeat=False): #note range, triad, given notes (as array of bare notes)
	def uniq(seq):
		# order preserving
		noDupes = []
		[noDupes.append(i) for i in seq if not noDupes.count(i)]
		return noDupes
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
	if norepeat:
		data = [sorted(set(val)) for val in itertools.product(*results)]
	else:
		data = [sorted(val) for val in itertools.product(*results)]
	return  uniq([val for val in data if len(val) == 4 and val[0] >= Ranges["bass"][0] and val[0] <= Ranges["bass"][1] and val[1] >= Ranges["tenor"][0] and val[1] <= Ranges["tenor"][1] and val[2] >= Ranges["alto"][0] and val[0] <= Ranges["alto"][1] and val[3] >= Ranges["soprano"][0] and val[0] <= Ranges["soprano"][1]])
def main():
	#print(findall(Triad(BareNote("C"),"halfdim7"),double=-1))
	notes = (
		(
			(Note('Eb3'), None, None, Note('G4')),
			Triad(BareNote('Eb'),'M')
		),
		(
			(Note('C3'), None, None, Note('G4')),
			Triad(BareNote('C'),'m')
		),
		(
			(Note('Ab2'), None, None, Note('Ab4')),
			Triad(BareNote('Ab'),'M')
		),
		(
			(Note('Bb2'), None, None, Note('F4')),
			Triad(BareNote('Bb'),'M')
		),
		(
			(Note('Eb3'), None, None, Note('Eb4')),
			Triad(BareNote('Eb'),'M')
		),
		(
			(Note('Eb3'), None, None, Note('G4')),
			Triad(BareNote('Eb'),'M')
		),
		(
			(Note('Bb2'), None, None, Note('F4')),
			Triad(BareNote('Bb'),'m')
		),
	)
	tree = Tree(None, True)
	main_loop(notes, tree, BareNote('G'))
	final_results = []
	def traverse(tree,data,initial=False):
		if not initial:
			data += (False) if tree.data == None else (tree.data,)
		if len(tree.children) == 0:
			final_results.append(list(data))
		else:
			for c in tree.children:
				traverse(c,data)
		print(data)
	traverse(tree,(),initial=True)
	final_results[:] = [val for val in final_results if len(val) == len(notes)]
	print("Complete!")
	for val in final_results:
		print(val)
def main_loop(notes, tree, key):
	if tree.index >= len(notes):
		return
	def checkparallel(a, b, interval):
		for x in range(0,len(a)):
			for y in range(x+1,len(a)):
				if a[y].num()-a[x].num() == interval and b[y].num()-b[x].num() == interval:
					print("Parallel "+str(interval)+" detected", a, b)
					return False
		return True
	def checkcrossover(a,b):
		if b[Voices['tenor']] >= a[Voices['bass']] and b[Voices['tenor']] <= a[Voices['alto']] and b[Voices['alto']] >= a[Voices['tenor']] and  b[Voices['alto']] <= a[Voices['soprano']]:
			return True
		else:
			print("Crossover!",a,b)
			return False
	def checkdoubling(notes,triad):
		double = triad.notes[0] #default
		if notes[Voices['bass']] == triad.notes[0]:
			double = triad.notes[0]
		elif triad.type == 'M' or triad.type == 'm':			
			if notes[Voices['bass']] == triad.notes[1]:
				double = a[Voices['soprano']]
		elif triad.type == 'dim' and notes[Voices['bass']] == triad.notes[1]:
			double = triad.notes[0]
		doublecount = 0
		for x in range(0,4):
			if notes[x].pitch() == double.pitch():
				doublecount = doublecount + 1
		return doublecount == 2
	def checklargeleaps(a, b, interval):
		for x in range(0,4):
			if abs(a[x].num()-b[x].num()) >= interval:
				return False
		return True
	def octaveorless(notes):
		return notes[Voices['soprano']].num() - notes[Voices['alto']].num() <= BareNote.intervals('P8') and notes[Voices['alto']].num() - notes[Voices['tenor']].num() <= BareNote.intervals('P8')
	two_filters = [ # True: success, False: failure
		["Parallel P1", lambda a,b: checkparallel(a, b, BareNote.intervals["P1"])],
		["Parallel P5", lambda a,b: checkparallel(a, b, BareNote.intervals["P5"])],
		["Parallel P8", lambda a,b: checkparallel(a, b, BareNote.intervals["P8"])],
		["Check crossover", checkcrossover],
		["Large leaps", lambda a,b: checklargeleaps(a, b, BareNote.intervals['m6'])],
	]
	p = findall(notes[tree.index][1])+findall(notes[tree.index][1],double=1)+findall(notes[tree.index][1],double=2)
	if notes[tree.index][0][Voices['bass']] != None:
		p[:] = [val for val in p if val[Voices['bass']] == notes[tree.index][0][Voices['bass']]]
		#print("Bass filter",p)
	if notes[tree.index][0][Voices['tenor']] != None:
		p[:] = [val for val in p if val[Voices['tenor']] == notes[tree.index][0][Voices['tenor']]]
		#print("Tenor filter",p)
	if notes[tree.index][0][Voices['alto']] != None:
		p[:] = [val for val in p if val[Voices['alto']] == notes[tree.index][0][Voices['alto']]]
		#print("Alto filter",p)
	if notes[tree.index][0][Voices['soprano']] != None:
		p[:] = [val for val in p if val[Voices['soprano']] == notes[tree.index][0][Voices['soprano']]]
		#print("Soprano filter",p)
	p[:] = [val for val in p if val[Voices['soprano']].num() - val[Voices['alto']].num() <= BareNote.intervals["P8"] and val[Voices['alto']].num() - val[Voices['tenor']].num() <= BareNote.intervals["P8"]] #check spacing
	if not tree.master:
		for rule in two_filters:
			p[:] = [val for val in p if rule[1](tree.data,val)]
	for val in p:
		main_loop(notes,tree.add(val), key)
if __name__ == "__main__":
	main()