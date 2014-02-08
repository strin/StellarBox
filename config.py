def readmap(path):
	config = file(path).readlines()
	config_map = dict()
	for line in config:
		line = line.replace('\n', '')
		line = line.replace('\r', '')
		line = line.split(':')
		key = line[0]
		for i in range(len(key)-1, -2, -1):
			if i == -1 or key[i] != ' ':
				break
		key = key[:i+1]
		value = line[1]
		for i in range(len(value)+1):
			if i == len(value) or value[i] != ' ':
				break
		value = value[i:]
		config_map[key] = value
	return config_map

def writemap(path, config_map):
	data = open(path, 'w')
	for key in config_map.keys():
		data.write(str(key)+':'+config_map[key]+'\n')