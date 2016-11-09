#!/bin/env python3
import argparse
import json
import os
import random
import time
from markov import Group, Model

def loop(model, delay = 0, timeout = 0, maxlen = 0, output_file = ''):
	group = model.random_group()
	start = time.time()

	print(group,end=' ')

	count = 0

	while (args.timeout == 0 or time.time() - start < args.timeout) and count <= maxlen:
		group = model.walk(group)

		if not group:
			break

		if output_file:
			with open(output_file, 'r') as f:
				print(group[-1],end=' ',flush=True, file = f)
		else:
			print(group[-1],end=' ',flush=True)

		if maxlen != 0:
			count +=1

		time.sleep(delay/1000)

	print()

def run(input_file, level = 1, use_model = False, output_text = '', save_model = '', merge = '', delay = 0, timeout = 0, maxlen = 0):
	settings = {}
	output_file = ''
	model_file = ''
	merge_model_file = ''
	data = None
	model = None
	merge_model = None

	with open('config.json', 'r') as f:
		settings = json.load(f)

	if use_model:
		input_file = os.path.join(settings['model_path'], input_file)
	else:
		input_file = os.path.join(settings['input_path'], input_file)
	if output_text:
		output_file = os.path.join(settings['output_path'], output_text)
	if save_model:
		model_file = os.path.join(settings['model_path'], save_model)
	if merge:
		merge_model_file = os.path.join(settings['model_path'], merge)

		with open(merge_model_file, 'r') as f:
			merge_model = Model(json.load(f))

	with open(input_file, 'r') as f:
		#treat as JSON
		if use_model:
			data = json.load(f)

		#treat as text
		else:
			data=f.read()
			data=Group(data.split(' '))

	model = Model(data, level)

	if merge:
		model += merge_model

	#Save model to file
	if save_model:
		with open(model_file, 'w') as f:
			json.dump(model.__dict__(), f)

	#run model indefinitely, print output
	else:
		loop(model, delay = delay, timeout = timeout, maxlen = maxlen, output_file = output_file)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', metavar = 'input_file', help = 'File with input data to be parsed')
	parser.add_argument('-m', action = 'store_true', help = 'Consider input file to be an existing model in JSON')
	parser.add_argument('-s', default = '', metavar = 'save_model', help = 'Filename for JSON model to be saved to')
	parser.add_argument('-o', default = '', metavar = 'output_text', help = 'File to output text to')
	parser.add_argument('-l', default = 1, type = int, metavar='level', help = 'Specify the level of the model (How many nodes per data group)')
	parser.add_argument('--delay', default = 0, type = float, help = 'time delay between print statements, in milliseconds')
	parser.add_argument('--timeout', default = 0, type = float, help = 'maximum running duration')
	parser.add_argument('--maxlen', default = 0, type = int, help = 'Maximum number of words in output')
	parser.add_argument('--merge', default = '', help = 'specify another model to merge with input_file')

	args = parser.parse_args()

	kwargs = vars(args)

	name_subs = {'m':'use_model', 's': 'save_model', 'o':'output_text', 'l': 'level'}
	for name, sub in name_subs.items():
		kwargs[sub] = kwargs[name]
		del kwargs[name]

	run(**kwargs)