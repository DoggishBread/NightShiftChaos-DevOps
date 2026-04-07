extends Node

@onready var label: Label = $Label
@onready var contador_fps: Label = $ContadorFPS

var score = 0

func addpoint ():
	score += 1
	label.text = str(score) + " NPCs cargados"

func _process(delta: float) -> void:
	contador_fps.text= str(Engine.get_frames_per_second())
