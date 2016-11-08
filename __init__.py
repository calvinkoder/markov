import random

class Group:
	def __init__(self, nodes = []):
		self.nodes = nodes

	def __str__(self):
		return ' '.join(self.nodes)

	def __getitem__(self, index):
		return self.nodes[index]

	def __len__(self):
		return len(self.nodes)

	def walk(self, next_node):
		self.nodes = self.nodes[1:]
		self.nodes.append(next_node)

	def sub(self, start, length):
		#prevent n greater than data len
		n=min(len(self), start+length)
		return Group(self[start:n])

class Model:
	model = {}
	node_count = {}
	def __init__(self, data, level = 1):
		self.level = level

		if type(data) == dict:
			self.model = data.get('model', {})
			self.level = data.get('level', level)
			self.node_count = data.get('node_count', {})
		else:
			self.generate(data, level)

	def __dict__(self):
		return {'model': self.model, 'node_count': self.node_count, 'level': self.level}

	def add_group(self, group_name):
		if not group_name in self.model:
			self.model[group_name] = {}
			self.node_count[group_name] = 0

		self.node_count[group_name] += 1

	def add_node(self, group_name, node):
		if node in self.model[group_name]:
			self.model[group_name][node] += 1
		else:
			self.model[group_name][node] = 1

	def generate(self, data, level=1):
		group = data.sub(0, level)

		for next_node in data[level:]:
			group_name = group.__str__()

			if next_node:
				self.add_group(group_name)
				self.add_node(group_name, next_node)

				group.walk(next_node)

		for group_name, group in self.model.items():
			for node, path_val in group.items():
				group[node] /= self.node_count[group_name]

	def walk(self, group):
		nodes=self.model.get(group.__str__(), None)

		if nodes:
			r=random.random()

			for node, odds in nodes.items():
				if odds>r:
					group.walk(node)
					return group
				else:
					r-=odds

		return None

	def random_group(self):
		group_name = random.choice(list(self.model.keys()))
		return Group(group_name.split(' '))