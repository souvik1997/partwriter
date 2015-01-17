#!/usr/bin/env python3
# partwriter.py - Automated part writing for four-part harmony
# Copyright (C) 2015 Souvik Banerjee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
#
#
# How it works:
# The core of the program is the findall method. It finds all combinations of a particular triad within the vocal
# ranges for each part. It finds possible notes for each voice and uses the Cartesian product to merge the voices
# together. All possible doubling arrangements are attempted. After concatenating these initial possiblities,
# the main loop attempts to match the list of possibiltiies with the user-provided list of notes. It then
# filters the list through the provided rules, adding a 'badness' factor which is an indicator of how bad a
# particular arrangement is. Once the final list of possible arrangements is obtained, each 4-note arrangement
# is added to the parent/child tree as children. Then the main loop recurses and uses each of the children as
# parent nodes for the next iteration until all user-provided triads have been parsed.
import itertools
import functools
import hashlib
import argparse
import logging
badness_config = {
	'threshold':"2500000",
	'parallel': "10000000",
	'crossover': "10000000",
	'smoothness': "lambda a: pow(2,a)",
	'doubling': "2500000",
	'largeleaps': "5000000",
	'octaveorless': "5000000",
	'leadingtone': "10000000",
	'tritone':"10000000"
}
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
	def bare_name(self):
		return self.letter()+self.accidental()
	def ascending_interval(self,invl):
		def search(s):
			res = []
			for k,v in BareNote.pitches.items():
				if v == s:
					res.append(k)
			return res
		carry = False
		if invl == "P8":
			return (BareNote(self.bare_name()),1)
		elif invl == "P1":
			return (BareNote(self.bare_name()),0)
		target = self.up_letter(int(invl[-1])-1)
		if "CDEFGAB".index(self.letter())+int(invl[-1]) > 7:
			carry = True
		new_pitch = (self.pitch() + BareNote.intervals[invl]) % 12 if carry else (self.pitch() + BareNote.intervals[invl])
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
		if len(ac) == 0:
			return ""
		if ac[-1] in ['0','1','2','3','4','5','6','7','8','9']:
			ac = ac[:-1]
		if len(ac) == 0 or ac not in ["##","#","b","bb"]:
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
	def __init__(self,root,type):
		self.type = type
		self.root = root
	def __str__(self):
		return str(self.notes())
	def __repr__(self):
		return self.__str__()
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
	def add(self,data,badness=0):
		tr = Tree(data)
		tr.depth = self.depth + 1
		tr.index = self.index + 1
		tr.parent = self
		tr.badness = self.badness + badness
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
progress = 0
def update_progress():
	global progress
	progress += 1
	print(".",end="",flush=True)
def main():
	tree = Tree(None, True)
	notes = []
	key = None
	parser = argparse.ArgumentParser(description='''
Automated part writing for four-part harmony.
Supports the following rules:
  Keep all voices in range
  Avoid parallel 5ths, octaves, and unisons
  Never double leading tone
  Double root when triad is in root position
  Double soprano when major/minor triads are in first inversion
  Double bass when diminished triads are in first inversion
  All factors of triads should be present
  Avoid large leaps of a 6th or more. Octave leaps are ok
  Maintain an octave or less between soprano and alto and between alto and tenor
  Do not crossover/overlap voices
  Avoid tritones
  Have each part flow smoothly (minimize skips)

Input files have the following format:
  Key: <note>
  [Notes]
  <bass>,<tenor>,<alto>,<soprano>,<triad root>:<triad type>
  <bass>,<tenor>,<alto>,<soprano>,<triad root>:<triad type>
  <bass>,<tenor>,<alto>,<soprano>,<triad root>:<triad type>
  ...

An example input file:
  Key: C
  [Notes]
  C3,  , G4,   , C:M
  C3,  , E4,   , C:M
    ,  ,   , D5, D:m
    ,  ,   , D5, G:M
    ,  ,   , C5, F:M
    ,  ,   , C5, C:M

The octave only needs to be specified for the bass, tenor, alto,
and soprano notes in the input file. The triad root and the key
should not have an octave specifier. The program will attempt to
find the best combination of notes to fill in the blanks. Spaces
and tabs are ignored, so they may be used for formatting.

You may specify how to weight infractions of the rules using 'badness' factors
(like in TeX) through command line arguments. The only exception is the calculation
of the badness value for smoothness. You can specify a python-style lambda on the
command line that will be used to calculate the badness value. The lambda should
take one argument and return an integer.

This program has a simple progress indicator to let you know that it is working.
Depending on the number of blanks given as input, the execution time will vary.
Before exiting, all possible solutions will be printed to the console, ranked from
the worst solution to the best (so that the best is on the bottom and can be read
on a terminal without scrolling up).
''', formatter_class=argparse.RawDescriptionHelpFormatter, epilog='Copyright (c) 2015 Souvik Banerjee. Released under GNU AGPLv3')
	parser.add_argument('-v','--verbose',action='store_true')
	parser.add_argument('inputfile',help="Input file", type=argparse.FileType('r'))
	for k,v in badness_config.items():
		if k == "smoothness":
			parser.add_argument("--"+k,help="badness function (as python lambda) for "+k+"(default: '%(default)s')",default=v)
		else:
			parser.add_argument("--"+k,help="badness value for "+k+"(default: '%(default)s')",default=v)
	args = parser.parse_args()
	for k in badness_config:
		badness_config[k] = eval('args.'+k)
	if args.verbose:
		logging.basicConfig(level=logging.DEBUG, format='%(message)s')
	else:
		logging.basicConfig(level=logging.INFO, format='%(message)s')
	with args.inputfile as f:
		first_line = f.readline().replace("Key:","").strip()
		key = BareNote(first_line)
		lines = f.readlines()
		for l in lines:
			if len(l.strip()) == 0 or l.strip() == "[Notes]":
				continue
			l=l.replace("-"," ")
			ns = l.split(",") #should be 5 elements (bass,tenor,alto,soprano,triad)
			val = [None, None, None, None]
			if ns[Voices['bass']].strip() != "":
				val[Voices['bass']] = Note(ns[Voices['bass']].strip())
			if ns[Voices['tenor']].strip() != "":
				val[Voices['tenor']] = Note(ns[Voices['tenor']].strip())
			if ns[Voices['alto']].strip() != "":
				val[Voices['alto']] = Note(ns[Voices['alto']].strip())
			if ns[Voices['soprano']].strip() != "":
				val[Voices['soprano']] = Note(ns[Voices['soprano']].strip())
			triad_note,triad_type = ns[Voices['soprano']+1].split(":")
			tr = Triad(BareNote(triad_note.strip()),triad_type.strip())
			notes.append([val,tr])
	print("Starting...")
	main_loop(notes, tree, key)
	print("") #new line
	final_results = []
	def traverse(tree,data,initial=False): #searches tree for complete solutions
		if not initial and tree.data != None: #first node has no data
			data += (tree.data,)
		if len(tree.children) == 0:
			final_results.append([tree.badness,list(data)])
		else:
			for c in tree.children:
				traverse(c,data)
		logging.debug("%s",data)
	traverse(tree,(),initial=True)
	final_results[:] = [val for val in final_results if len(val[1]) == len(notes)] #sanity check
	final_results.sort(key=lambda a: a[0],reverse=True)
	print("Complete! Listing solutions:")
	print("Format: badness, notes, hash")
	print(len(final_results),"complete solutions")
	for val in final_results:
		print(val[0],val[1],hashlib.md5(str(val[1]).encode()).hexdigest()[:7])
def main_loop(notes, tree, key_root):
	update_progress()
	if tree.index >= len(notes):
		return
	if len(notes[tree.index][1].notes()) == 3:
		p = findall(notes[tree.index][1])+findall(notes[tree.index][1],double=1)+findall(notes[tree.index][1],double=2)
	else:
		p = findall(notes[tree.index][1],double=-1)
	if notes[tree.index][0][Voices['bass']] != None:
		p[:] = [val for val in p if val[Voices['bass']] == notes[tree.index][0][Voices['bass']]]
	if notes[tree.index][0][Voices['tenor']] != None:
		p[:] = [val for val in p if val[Voices['tenor']] == notes[tree.index][0][Voices['tenor']]]
	if notes[tree.index][0][Voices['alto']] != None:
		p[:] = [val for val in p if val[Voices['alto']] == notes[tree.index][0][Voices['alto']]]
	if notes[tree.index][0][Voices['soprano']] != None:
		p[:] = [val for val in p if val[Voices['soprano']] == notes[tree.index][0][Voices['soprano']]]
	p[:] = [[val,0] for val in p] #default badness = 0
	if not tree.master:
		for rule in two_filters:
			for val in p:
				val[1] += rule[1](tree.data,val[0])
	for rule in one_filters:
		for val in p:
			val[1] += rule[1](val[0],notes[tree.index][1],key_root)
	for val in p:
		if val[1] < int(badness_config['threshold']):
			new_node = tree.add(val[0],val[1])
			main_loop(notes,new_node, key_root)
#Rules:
def checkparallel(a, b, interval):
	badness = int(badness_config['parallel']) #Very bad!
	for x in range(0,len(a)):
		for y in range(x+1,len(a)):
			if a[y].num()-a[x].num() == interval and b[y].num()-b[x].num() == interval and a[y].num() != b[y].num() and a[x].num() != b[x].num():
				logging.debug("Parallel %s detected: %s %s", str(interval), a, b)
				return badness
	return 0
def checkcrossover(a,b):
	badness = int(badness_config['crossover']) #Very bad!
	if b[Voices['tenor']] >= a[Voices['bass']] and b[Voices['tenor']] <= a[Voices['alto']] and b[Voices['alto']] >= a[Voices['tenor']] and  b[Voices['alto']] <= a[Voices['soprano']]:
		return 0
	else:
		logging.debug("Crossover! %s %s",a,b)
		return badness
def checksmoothness(a,b):
	badness = 0
	for x in range(0,4):
		badness += eval(badness_config['smoothness'])(abs(a[x].num()-b[x].num()))
	return badness
def checkdoubling(notes,triad):
	badness = int(badness_config['doubling'])
	if len(triad.notes()) != 3:
		return 0
	double = notes[Voices['bass']] #default is the bass
	toprint = ""
	if notes[Voices['bass']].pitch() == triad.note(0).pitch():
		toprint = 'root position: '+str(notes)+", "+str(triad.notes())
		double = triad.note(0)
	elif triad.type == 'M' or triad.type == 'm':
		if notes[Voices['bass']].pitch() == triad.note(1).pitch():
			toprint = '1st inversion, major or minor: '+str(notes)+", "+str(triad.notes())
			double = notes[Voices['soprano']]
	elif triad.type == 'dim' and notes[Voices['bass']].pitch() == triad.note(1).pitch():
		toprint = 'diminished, first inversion: '+str(notes)+", "+str(triad.notes())
		double = triad.note(0)
	doublecount = 0
	for x in range(0,4):
		if notes[x].pitch() == double.pitch():
			doublecount = doublecount + 1
	if doublecount == 2:
		return 0
	else:
		if toprint == "":
			logging.debug('Doubling Error! ? %s %s',notes,triad.notes())
		else:
			logging.debug('Doubling Error! %s',toprint)
		return badness
def checklargeleaps(a, b, interval):
	badness = int(badness_config['largeleaps'])
	for x in range(0,4):
		if abs(a[x].num()-b[x].num()) >= interval and abs(a[x].num()-b[x].num()) != BareNote.intervals['P8']:
			logging.debug("Large leap! %s %s",a,b)
			return badness
	return 0
def check_tritone(a,b):
	badness = int(badness_config['tritone'])
	for x in range(0,4):
		if abs(a[x].num()-b[x].num()) == BareNote.intervals["A4"]:
			logging.debug("Tritone! %s %s",a,b)
			return badness
	return 0
def octaveorless(notes):
	badness = int(badness_config['octaveorless'])
	res = notes[Voices['soprano']].num() - notes[Voices['alto']].num() <= BareNote.intervals['P8'] and notes[Voices['alto']].num() - notes[Voices['tenor']].num() <= BareNote.intervals['P8']
	if not res:
		logging.debug("Soprano/alto or alto/tenor are more than an octave apart! %s",notes)
		return badness
	return 0
def checkleadingtone(notes, key_root):
	badness = int(badness_config['leadingtone'])
	count = 0
	for x in range(0,4):
		if notes[x].pitch() == key_root.ascending_interval("M7")[0].pitch():
			count = count + 1
	if count < 2:
		return 0
	else:
		logging.debug("Too many leading tones! %s",notes)
		return badness
one_filters = [ #notes, triad, key
	["Doubling", lambda a,b,c: checkdoubling(a,b)],
	["Octave or less", lambda a,b,c: octaveorless(a)],
	["Leading tone", lambda a,b,c: checkleadingtone(a,c)],
]
two_filters = [ # notes #1, notes #2
	["Parallel P1", lambda a,b: checkparallel(a, b, BareNote.intervals["P1"])],
	["Parallel P5", lambda a,b: checkparallel(a, b, BareNote.intervals["P5"])],
	["Parallel P8", lambda a,b: checkparallel(a, b, BareNote.intervals["P8"])],
	["Check crossover", checkcrossover],
	["Large leaps", lambda a,b: checklargeleaps(a, b, BareNote.intervals['m6'])],
	["Smoothness", checksmoothness],
	["Tritone",check_tritone]
]
if __name__ == "__main__":
	main()