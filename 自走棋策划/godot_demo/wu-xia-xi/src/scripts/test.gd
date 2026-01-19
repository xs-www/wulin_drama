extends Node2D

func _ready() -> void:
	print(Utils.matrix_mutiply([[1,2,3],[2,3,4]], [[2,3,4],[3,4,5]]))
