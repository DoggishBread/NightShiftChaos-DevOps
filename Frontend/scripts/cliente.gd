extends CharacterBody3D

enum Estado { IR_A_PASILLO, ESPERAR_PASILLO, IR_A_CAJA, ESPERAR_PAGO, SALIR }
var estado_actual = Estado.IR_A_PASILLO

const SPEED = 3.0
var tiempo_en_caja = 0.0
var destino_actual = Vector3.ZERO
var fuerza_empuje = Vector3.ZERO

@onready var nav_agent = $NavigationAgent3D
@onready var modelo_visual = $"character-male-d2"

func _ready():
	add_to_group("clientes")
	randomize()
	await get_tree().physics_frame
	ir_a_estante()

func _physics_process(delta):
	if estado_actual == Estado.ESPERAR_PAGO:
		tiempo_en_caja += delta
		if tiempo_en_caja >= 5.0:
			get_node("/root/main/game_manager").registrar_error_impaciencia()
			atender_cliente() 
			
		velocity = Vector3.ZERO + fuerza_empuje
		fuerza_empuje = fuerza_empuje.lerp(Vector3.ZERO, delta * 5.0)
		move_and_slide()
		return
		
	if estado_actual == Estado.ESPERAR_PASILLO:
		velocity = Vector3.ZERO + fuerza_empuje
		fuerza_empuje = fuerza_empuje.lerp(Vector3.ZERO, delta * 5.0)
		move_and_slide()
		return
		
	if nav_agent.is_navigation_finished():
		if estado_actual == Estado.IR_A_PASILLO:
			esperar_en_estante()
		elif estado_actual == Estado.SALIR:
			queue_free()
		
		velocity = Vector3.ZERO + fuerza_empuje
		fuerza_empuje = fuerza_empuje.lerp(Vector3.ZERO, delta * 5.0)
		move_and_slide()
		return
		
	var posicion_actual = global_position
	var siguiente_posicion = nav_agent.get_next_path_position()
	
	var direccion = posicion_actual.direction_to(siguiente_posicion)
	direccion.y = 0.0
	
	if direccion.length() > 0:
		direccion = direccion.normalized()
	else:
		direccion = Vector3.ZERO
		
	fuerza_empuje = fuerza_empuje.lerp(Vector3.ZERO, delta * 5.0)
	velocity = (direccion * SPEED) + fuerza_empuje
	
	if direccion.length() > 0.1:
		var look_target = global_position + direccion
		modelo_visual.look_at(look_target, Vector3.UP)
		modelo_visual.rotate_y(PI) 
		
	move_and_slide()
	
	for i in get_slide_collision_count():
		var colision = get_slide_collision(i)
		var otro = colision.get_collider()
		
		if otro and otro.is_in_group("clientes"):
			var direccion_rebote = (global_position - otro.global_position).normalized()
			direccion_rebote.y = 0.0
			fuerza_empuje += direccion_rebote * 1.5

func recibir_empujon(direccion_impacto: Vector3, fuerza: float):
	fuerza_empuje += direccion_impacto * fuerza

func ir_a_estante():
	estado_actual = Estado.IR_A_PASILLO
	var waypoints = get_tree().get_nodes_in_group("waypoints")
	if waypoints.size() > 0:
		var destino_random = waypoints[randi() % waypoints.size()]
		nav_agent.target_position = destino_random.global_position

func esperar_en_estante():
	estado_actual = Estado.ESPERAR_PASILLO
	await get_tree().create_timer(5.0).timeout
	ir_a_caja()

func ir_a_caja():
	estado_actual = Estado.IR_A_CAJA
	var cajas = get_tree().get_nodes_in_group("caja_registradora")
	var todos_los_clientes = get_tree().get_nodes_in_group("clientes")
	
	var mejor_caja = null
	var menor_fila = 9999
	
	for caja in cajas:
		var personas_en_esta_fila = 0
		for c in todos_los_clientes:
			if c != self and c.estado_actual in [Estado.IR_A_CAJA, Estado.ESPERAR_PAGO] and c.destino_actual == caja.global_position:
				personas_en_esta_fila += 1
				
		if personas_en_esta_fila < menor_fila:
			menor_fila = personas_en_esta_fila
			mejor_caja = caja
			
	if mejor_caja:
		destino_actual = mejor_caja.global_position
		nav_agent.target_position = destino_actual

func atender_cliente():
	estado_actual = Estado.SALIR
	var salidas = get_tree().get_nodes_in_group("puerta_salida")
	if salidas.size() > 0:
		nav_agent.target_position = salidas[0].global_position
