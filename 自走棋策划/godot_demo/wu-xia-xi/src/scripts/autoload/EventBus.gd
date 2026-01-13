# EventBus.gd
## 全局事件总线（Global Event Bus）
## 作为 AutoLoad 使用，任何地方通过 EventBus.on() / emit() 实现完全解耦的消息通信。
extends Node

## 是否打印事件分发日志（仅 debug 用）
@export var DEBUG := true
## 若为 true，emit 时会通过 call_deferred 把回调推进主线程，避免多线程 emit 导致崩溃。
@export var THREAD_SAFE := true
## 事件名 -> Signal 映射表，运行时自动扩容，无需提前注册。
var _signals : Dictionary = {}

## 永久监听事件
## @param event_name : 事件名，推荐用 snake_case，例如 "enemy_died"
## @param callback   : 回调函数，签名 func(data: Dictionary)，data 由 emit 方决定
func on(event_name: StringName, callback: Callable) -> void:
	_get_or_creat(event_name).connect(callback)
	if DEBUG: prints("[EventBus] on:", event_name, "callback:", callback)
	pass

## 一次性监听：事件触发后自动取消注册
## 用法与 on() 完全相同，但回调只会执行一次
func once(event_name: StringName, callback: Callable) -> void:
	var wrapper : Callable
	wrapper = func(context=[]):
		off(event_name, wrapper)	# 先删，确保只执行一次
		callback.callv(context)		# 再调用用户真正逻辑
	on(event_name, wrapper)
	pass

## 取消监听
## @param callback 必须与当初 on()/once() 传入的 **同一 Callable**，否则无法断开
func off(event_name: StringName, callback: Callable) -> void:
	var sig : Signal = _signals.get(event_name)
	if sig and sig.is_connected(callback):
		sig.disconnect(callback)
		if DEBUG:
			prints("[EventBus] off:", event_name, "callback:", callback)
	pass

## 派发事件
## @param event_name : 要触发的事件名
## @param args       : 任意字典，携带数据给监听者；建议 key 用 snake_case
func emit(event_name: StringName, context: Dictionary = {}) -> void:
	if DEBUG:
		prints("[EventBus] emit:", event_name, "context:", context)
	var sig : Signal = _get_or_creat(event_name)
	if not sig:
		if DEBUG:
			prints("[EventBus] 无监听者，事件被忽略:", event_name)
		return
	
	if THREAD_SAFE:
		call_deferred("_do_emit", sig, context)
	else:
		_do_emit(sig, context)
	pass
	
## 获取或动态创建 Signal
## @return 与 event_name 绑定的 Signal 实例
func _get_or_creat(event_name: StringName) -> Signal:
	if not _signals.has(event_name):
		_signals[event_name] = Signal()
	return _signals[event_name]

## 真正执行 emit 的地方
## 分离出来是为了支持 call_deferred
func _do_emit(sig: Signal, context: Dictionary) -> void:
	sig.emit(context)
