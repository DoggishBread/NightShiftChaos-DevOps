extends CharacterBody3D

const SPEED = 3.0

@onready var nav_agent = $NavigationAgent3D
@onready var modelo_visual = $"character-male-d2"

func _ready():

	var posicion_caja_1 = Vector3(3.0, 0.0, -1.0)
	var posicion_caja_2 = Vector3(3.0, 0.0, -3.0)
	
	var lista_de_cajas = [posicion_caja_1, posicion_caja_2]

	var caja_elegida = lista_de_cajas.pick_random()

	nav_agent.target_position = caja_elegida

func _physics_process(delta):
	if nav_agent.is_navigation_finished():
		velocity = Vector3.ZERO
		move_and_slide()
		return
		
	var posicion_actual = global_position
	var siguiente_posicion = nav_agent.get_next_path_position()
	
	var direccion = posicion_actual.direction_to(siguiente_posicion)
	direccion.y = 0.0
	direccion = direccion.normalized()
	
	velocity = direccion * SPEED
	
	var look_target = global_position + direccion
	if global_position.distance_to(look_target) > 0.1:
		modelo_visual.look_at(look_target, Vector3.UP)
		modelo_visual.rotate_y(PI) 
		
	move_and_slide()
