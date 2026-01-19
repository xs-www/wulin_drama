extends Node

class_name Utils

static func load_json(file_path):
	var file = FileAccess.open(file_path, FileAccess.READ)
	var json = JSON.new()
	var data = file.get_as_text()
	if json.parse(data) == OK:
		return json.data
	return null
		
static func load_character_from_json(file_path = "res://src/data/character_config.json", char_id = 1):
	var char_data: Dictionary = load_json(file_path)
	if char_data:
		return char_data.get(char_id)
	else:
		return null
		
static func merge_dicts(dict_list: Array[Dictionary]):
	var res = {}
	for dict in dict_list:
		for k in dict.keys():
			if k in res:
				if typeof(dict[k]) in [Variant.Type.TYPE_INT, Variant.Type.TYPE_FLOAT]:
					
					pass
				elif typeof(res[k] in [Variant.Type.TYPE_ARRAY]):
					pass
	pass
	
func load_data_to_saves(file_path, save_id):
	pass
	
static func matrix_mutiply(mat1 : Array[Array], mat2: Array[Array]):
	var res = mat1.duplicate()
	for i in range(len(mat1)):
		for j in range(len(mat1[i])):
			res[i][j] = mat1[i][j] * mat2[i][j]
	return res
