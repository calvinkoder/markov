import argparse
import json
import os
import random
import time
from markov import Group, Model

parser = argparse.ArgumentParser()
parser.add_argument('input_file', metavar = 'input_file', help = 'File with input data to be parsed')
parser.add_argument('-m', action = 'store_true', help = 'Consider input file to be an existing model in JSON')
parser.add_argument('-S', default = '', metavar = 'save_model', help = 'Filename for JSON model to be saved to')
parser.add_argument('-o', default = '', metavar = 'save_model', help = 'File to output text to')
parser.add_argument('-l', default = 1, type = int, metavar='level', help = 'Specify the level of the model (How many nodes per data group)')
parser.add_argument('-delay', default = 0, type = float, help = 'time delay between print statements, in milliseconds')
parser.add_argument('-timeout', default = 0, type = float, help = 'maximum running duration')
parser.add_argument('-maxlen', default = 0, type = int, help = 'Maximum number of words in output')

settings = {}
with open('config.json', 'r') as f:
	settings = json.load(f)

args = parser.parse_args()

input_file = os.path.join(settings['input_path'], args.input_file)
output_file = os.path.join(settings['output_path'], args.o)
model_file = os.path.join(settings['model_path'], args.S)

print(input_file)

data = None
m = None

if args.m:
	input_file = os.path.join(settings['model_path'], args.input_file)

with open(input_file, 'r') as f:
	#treat as JSON
	if args.m:
		data = json.load(f)

	#treat as text
	else:
		data=f.read()
		data=Group(data.split(' '))

m=Model(data, args.l)

#Save model to file
if args.S:
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