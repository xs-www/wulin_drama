extends Node2D

func _ready() -> void:
	EventBus.emit("test_sig")
