## 全局事件管理器
## 使用方式：
##   装饰器：@EventBus.on("event_name")
##   直接注册：EventBus.register("event_name", callback)
##   触发事件：EventBus.broadcast("event_name", key=value)
extends Node

@export var DEBUG := true
@export var THREAD_SAFE := true

# 事件监听器字典，结构：{事件名: [回调函数1, 回调函数2, ...]}
var listeners : Dictionary = {}

# 用于跟踪一次性监听器的包装器
var _once_wrappers : Dictionary = {}

func _init():
	if DEBUG:
		prints("[EventBus] 事件管理器初始化成功。")

## === 核心四个函数 ===

## 注册事件监听器
func register(event_name: StringName, callback: Callable) -> void:
	"""
	直接注册事件监听器
	:param event_name: 事件名称
	:param callback: 回调函数，函数签名需匹配事件参数
	"""
	if not event_name in listeners:
		listeners[event_name] = []
	
	listeners[event_name].append(callback)
	
	if DEBUG:
		prints("[EventBus] 注册事件:", event_name, "回调:", _get_callback_name(callback))

## 注销事件监听器
func unregister(event_name: StringName, callback: Callable) -> void:
	"""
	注销事件监听器
	:param event_name: 事件名称
	:param callback: 需移除的回调函数
	"""
	if event_name in listeners:
		var index = listeners[event_name].find(callback)
		if index != -1:
			listeners[event_name].remove_at(index)
			
			# 清理一次性监听器的映射
			if _once_wrappers.has(callback):
				_once_wrappers.erase(callback)
			
			if DEBUG:
				prints("[EventBus] 注销事件:", event_name, "回调:", _get_callback_name(callback))
		
		# 如果事件没有监听器了，清理数组
		if listeners[event_name].size() == 0:
			listeners.erase(event_name)

## 广播（触发）事件
func broadcast(event_name: StringName, context: Dictionary) -> void:
	"""
	广播（触发）事件，将 context 作为参数传递给所有监听器
	:param event_name: 事件名称
	:param context: 任意关键字参数
	"""
	if DEBUG:
		prints("[EventBus] 事件触发:", event_name, "参数:", context)
	
	if not event_name in listeners:
		if DEBUG:
			prints("[EventBus] 事件无监听者:", event_name)
		return
	
	# 获取当前监听器的副本，避免在迭代时修改
	var callbacks = listeners[event_name].duplicate()
	
	if THREAD_SAFE:
		call("_execute_callbacks", callbacks, context)
	else:
		_execute_callbacks(callbacks, context)
		
func _execute_callbacks(callbacks, context: Dictionary) -> void:
	"""执行所有回调函数"""
	for callback in callbacks:
		if callback.is_valid():
			# 将字典参数转换为关键字参数
			callback.callv(context.values())
		elif DEBUG:
			prints("[EventBus] 无效回调，跳过:", _get_callback_name(callback))

func _get_callback_name(callback: Callable) -> String:
	"""获取回调函数的名称（用于调试）"""
	if callback.is_custom():
		return "自定义回调"
	elif callback.is_standard():
		return callback.get_method()
	return "未知回调"
