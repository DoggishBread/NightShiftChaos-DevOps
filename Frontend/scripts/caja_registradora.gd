extends Area3D

@onready var http_request = $HTTPRequest
@onready var game_manager = get_node("/root/main/game_manager")

var jugador_cerca = false
var cliente_en_caja = null

func _ready():
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body):
	if body.name == "Player":
		jugador_cerca = true
		print("Cajero en posicion.")
	elif body.has_method("atender_cliente") and body.estado_actual == body.Estado.IR_A_CAJA:
		body.estado_actual = body.Estado.ESPERAR_PAGO
		cliente_en_caja = body
		print("Cliente en caja listo para pagar.")

func _on_body_exited(body):
	if body.name == "Player":
		jugador_cerca = false
	elif body == cliente_en_caja:
		cliente_en_caja = null

func _input(event):
	# Solo ejecutamos acciones si el cajero esta en esta caja especifica
	if jugador_cerca and event.is_action_pressed("ui_accept"):
		if cliente_en_caja != null:
			game_manager.registrar_venta()
			enviar_compra()
			cliente_en_caja.atender_cliente()
			cliente_en_caja = null
		else:
			print("No hay clientes esperando en esta caja.")

func enviar_compra():
	print("Enviando transaccion a la base de datos...")
	var url = "https://aplitic-rainily-karan.ngrok-free.dev/comprar"
	
	var datos = {
		"producto": "Hamburguesa",
		"precio": 120.0
	}
	
	var json_datos = JSON.stringify(datos)
	var headers = ["Content-Type: application/json"]
	
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, json_datos)
	
	if error != OK:
		print("Hubo un problema de conexion con la API")
