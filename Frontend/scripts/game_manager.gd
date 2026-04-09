extends Node

var escena_cliente = preload("res://Scenes/cliente.tscn")
var ventas_acomuladas = 0
var errores_acomulados = 0
var guardando = false

@onready var contador_de_npc: Node = $"../Cosas Camara/Camera3D/Contador de NPC"
@onready var timer_spawneo: Timer = $"../Extras/TimerSpawneo"
@onready var http_request: HTTPRequest = $HTTPRequest
@onready var punto_spawn = $"../Extras/PuntoSpawn"
@onready var sonido_caja = $SonidoCaja
@onready var sonido_error = $SonidoError

func _ready():
	get_tree().set_auto_accept_quit(false)
	timer_spawneo.timeout.connect(_on_timer_timeout)

func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		enviar_partida_al_servidor()

func _on_timer_timeout():
	var nuevo_cliente = escena_cliente.instantiate()
	add_child(nuevo_cliente)
	
	nuevo_cliente.global_position = punto_spawn.global_position
	contador_de_npc.addpoint()

func _input(event):
	if event.is_action_pressed("cometer_error"):
		errores_acomulados += 1
		sonido_error.play()
		print("Error registrado. Llevas: ", errores_acomulados)

	if event.is_action_pressed("ui_cancel"):
		enviar_partida_al_servidor()

func registrar_venta():
	ventas_acomuladas += 1
	sonido_caja.play()
	print("Venta registrada. Llevas: ", ventas_acomuladas)

func enviar_partida_al_servidor():
	if guardando:
		return
		
	if ventas_acomuladas == 0 and errores_acomulados == 0:
		cerrar_o_reiniciar()
		return

	guardando = true
	print("Enviando reporte de turno al servidor...")
	var url = "https://aplitic-rainily-karan.ngrok-free.dev/guardar_partida"

	var datos = {
		"usuario": "Ram_Admin",
		"ventas": ventas_acomuladas,
		"errores": errores_acomulados
	}

	var json_datos = JSON.stringify(datos)
	var headers = ["Content-Type: application/json"]

	if not http_request.request_completed.is_connected(_on_request_completed):
		http_request.request_completed.connect(_on_request_completed)
		
	http_request.request(url, headers, HTTPClient.METHOD_POST, json_datos)

func _on_request_completed(result, response_code, headers, body):
	print("Servidor respondio con codigo: ", response_code)
	cerrar_o_reiniciar()

func cerrar_o_reiniciar():
	if OS.has_feature("web"):
		print("Entorno web: Recargando nivel")
		get_tree().reload_current_scene()
	else:
		print("Entorno escritorio: Cerrando juego")
		get_tree().quit()

func registrar_error_impaciencia():
	errores_acomulados += 1
	sonido_error.play()
	print("¡Un cliente se hartó de esperar y se fue! Errores: ", errores_acomulados)
