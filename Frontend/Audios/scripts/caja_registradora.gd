extends Area3D

@onready var http_request = $HTTPRequest
var jugador_cerca = false

func _ready():
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body):
	if body.name == "Player":
		jugador_cerca = true
		print("Presiona ACEPTAR para procesar la venta")

func _on_body_exited(body):
	if body.name == "Player":
		jugador_cerca = false

func _input(event):
	# Si el jugador esta cerca y presiona Enter o Espacio
	if jugador_cerca and event.is_action_pressed("ui_accept"):
		enviar_compra()

func enviar_compra():
	print("Enviando transaccion a la base de datos...")
	var url = "http://127.0.0.1:5000/comprar"
	
	var datos = {
		"producto": "Hamburguesa",
		"precio": 120.0
	}
	
	var json_datos = JSON.stringify(datos)
	var headers = ["Content-Type: application/json"]
	
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, json_datos)
	
	if error != OK:
		print("Hubo un problema de conexion con la API")
