#!/bin/env python3
import argparse
import json
import os
import random
import time
from markov import Group, Model

settings = {}
input_file = ''
output_file = ''
model_file = ''
merge_model_file = ''
data = None
m = None
merge_m = None

parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar = 'input_file', help = 'File with input data to be parsed')
parser.add_argument('-m', action = 'store_true', help = 'Consider input file to be an existing model in JSON')
parser.add_argument('-s', default = '', metavar = 'save_model', help = 'Filename for JSON model to be saved to')
parser.add_argument('-o', default = '', metavar = 'save_model', help = 'File to output text to')
parser.add_argument('-l', default = 1, type = int, metavar='level', help = 'Specify the level of the model (How many nodes per data group)')
parser.add_argument('--delay', default = 0, type = float, help = 'time delay between print statements, in milliseconds')
parser.add_argument('--timeout', default = 0, type = float, help = 'maximum running duration')
parser.add_argument('--maxlen', default = 0, type = int, help = 'Maximum number of words in output')
parser.add_argument('--merge', default = '', help = 'specify another model to merge with input_file')

args = parser.parse_args()

with open('config.json', 'r') as f:
	settings = json.load(f)

if args.m:
	input_file = os.path.join(settings['model_path'], args.input_file)
else:
	input_file = os.path.join(settings['input_path'], args.input_file)
if args.o:
	output_file = os.path.join(settings['output_path'], args.o)
if args.s:
	model_file = os.path.join(settings['model_path'], args.s)
if args.merge:
	merge_model_file = os.path.join(settings['model_path'], args.merge)

	with open(merge_model_file, 'r') as f:
		merge_m = Model(json.load(f))

with open(input_file, 'r') as f:
	#treat as JSON
	if args.m:
		data = json.load(f)

	#treat as text
	else:
		data=f.read()
		data=Group(data.split(' '))

m=Model(data, args.l)

if args.merge:
	m += merge_m

#Save model to file
if args.s:
	with open(model_file, 'w') as f:
		json.dump(m.__dict__(), f)

#run model indefinitely, print output
else:
	group = m.random_group()
	start = time.time()

	print(group,end=' ')

	count = 0

	while (args.timeout == 0 or time.time() - start < args.timeout) and count <= args.maxlen:
		group = m.walk(group)

		if not group:
			break

		if args.o:
			with open(output_file, 'r') as f:
				print(group[-1],end=' ',flush=True, file = f)
		else:
			print(group[-1],end=' ',flush=True)

		if args.maxlen != 0:
			count +=1

		time.sleep(args.delay/1000)

	print()