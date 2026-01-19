extends Resource

## 角色资源基类
class_name CharacterSrc

@export var character_id : int
@export var charatcer_name : String

@export var health_points: float
@export var attack_power: float
@export var speed: float
@export var armor: int
@export var energy: int
@export var initiative: int

func load_from_json(file_path, char_id):
	pass
