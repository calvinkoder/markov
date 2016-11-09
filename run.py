#!/bin/env python3
import argparse
import json
import os
import random
import time
from markov import Group, Model

CONFIG_FILE = None

def loop(model, delay = 0, timeout = 0, maxlen = 0, output_file = ''):
	group = model.random_group()
	start = time.time()

	print(group,end=' ')

	count = 0

	while (timeout == 0 or time.time() - start < timeout) and count <= maxlen:
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

def run(model, output_file = '', output_as_model = False, merge_model = None,  delay = 0, timeout = 0, maxlen = 0):
	if merge_model:
		model += merge_model

	#Save model to file
	if output_as_model:
		with open(output_file, 'w') as f:
			json.dump(model.__dict__(), f)

	#run model indefinitely, print output
	else:
		loop(model, delay = delay, timeout = timeout, maxlen = maxlen, output_file = output_file)

def load_input(input_file, input_as_model = False):
	with open(input_file, 'r') as f:
		#treat as JSON
		if input_as_model:
			return json.load(f)

		#treat as text
		else:
			data = f.read()
			return Group(data.split(' '))

def main(input_file, settings = {}, input_as_model = False, output_file = '', output_as_model = False, merge_model_file = '', level = 1, delay = 0, timeout = 0, maxlen = 0):
	merge_model = None

	if input_as_model:
		input_file = os.path.join(settings.get('model_path', ''), input_file)
	else:
		input_file = os.path.join(settings.get('input_path', ''), input_file)
	if output_as_model:
		model_file = os.path.join(settings.get('model_path', ''), output_file)
	elif output_file:
		output_file = os.path.join(settings.get('output_path', ''), output_file)
	if merge_model_file:
		merge_model_file = os.path.join(settings.get('model_path', ''), merge)

		with open(merge_model_file, 'r') as f:
			merge_model = Model(json.load(f))

	model = Model(load_input(input_file), level)
	run(model, output_file, output_as_model, merge_model, level, delay, timeout, maxlen)

if __name__ == '__main__':
	CONFIG_FILE = 'config.json'

	parser = argparse.ArgumentParser()
	parser.add_argument('input_file', help = 'File with input data to be parsed')
	parser.add_argument('-m', action = 'store_true', help = 'Consider input file to be an existing model in JSON')
	parser.add_argument('-s', default = '', help = 'File for JSON model to be saved to')
	parser.add_argument('-o', default = '', help = 'File to output text to')
	parser.add_argument('-l', default = 1, type = int, help = 'Specify the level of the model (How many nodes per data group)')
	parser.add_argument('--delay', default = 0, type = float, help = 'time delay between print statements, in milliseconds')
	parser.add_argument('--timeout', default = 0, type = float, help = 'maximum running duration')
	parser.add_argument('--maxlen', default = 0, type = int, help = 'Maximum number of words in output')
	parser.add_argument('--merge', default = '', help = 'specify another model to merge with input_file')

	args = parser.parse_args()

	kwargs = vars(args)

	name_subs = {'m':'input_as_model', 'l': 'level', 'merge': 'merge_model_file'}
	for name, sub in name_subs.items():
		kwargs[sub] = kwargs[name]
		del kwargs[name]

	if args.s:
		kwargs['output_file'] = args.s
		kwargs['output_as_model'] = True
	else:
		kwargs['output_file'] = args.o
		kwargs['output_as_model'] = False

	del kwargs['s']
	del kwargs['o']

	with open(CONFIG_FILE, 'r') as f:
		kwargs['settings'] = json.load(f)

	main(**kwargs)