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

		if data:
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
			if next_node:
				group_name = group.__str__()

				self.add_group(group_name)
				self.add_node(group_name, next_node)

				group.walk(next_node)

		for group_name, group in self.model.items():
			for node, path_val in group.items():
				group[node] /= self.node_count[group_name]

	def __add__(self, _model):
		new_model = Model({}, self.level)

		if self.level == _model.level:
			for group_name, group in self.model.items():
				self_count = self.node_count[group_name]
				total_count = self_count
				_model_count = 0

				if _model.model.get(group_name, None):
					_model_count = _model.node_count[group_name]
					total_count += _model_count

				for node, self_path_val in group.items():

					new_model.add_group(group_name)

					#common group
					if self.model.get(group_name, None):

						#common node -> average values
						if node in _model.model.get(group_name, {}):
							new_model.model[group_name][node] = (self_count * self_path_val + _model_count * _model.model[group_name][node])/total_count
						
						#exclusive node
						else:
							new_model.model[group_name][node] = self_path_val * self_count / total_count
					else:
						new_model.model[group_name][node] = self_path_val

					new_model.node_count[group_name] = total_count

			#add remaining items exclusively in _model
			for group_name, group in _model.model.items():
				for node, path_val in group.items():
					#common group
					if self.model.get(group_name, None):
						#exclusive node
						if not node in self.model.get(group_name, {}):
							new_model.model[group_name][node] = path_val*_model.node_count[group_name]/new_model.node_count[group_name]
					#exclusive group
					else:
						new_model.add_group(group_name)
						new_model.model[group_name][node] = path_val

		return new_model

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