extends ProgressBar

var sum_delta : float = 0

func _ready():
	value = 100
	print("设置value为100")

func _process(delta: float) -> void:
	sum_delta += delta
	if sum_delta >= 1:
		value -= 10
		print(value)
		sum_delta = 0
