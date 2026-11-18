from limpieza_correo import limpiar_texto_correo


def test_quita_el_bloque_citado_con_escribio():
    texto = (
        "Hola, quiero confirmar el pedido de ayer.\n\n"
        "El mié, 18 nov 2026 a las 17:09, Panadería Luz <panaderialuz@ejemplo.com> escribió:\n"
        "> Buenas, ¿podrías confirmarnos el pedido?\n"
        "> Gracias\n"
    )
    assert limpiar_texto_correo(texto) == "Hola, quiero confirmar el pedido de ayer."


def test_quita_la_firma():
    texto = (
        "Buenas tardes, necesito 3 cajas de tomates para el jueves.\n"
        "--\n"
        "Marta Ruiz\n"
        "Restaurante El Horno\n"
        "Tel: 600111222\n"
    )
    assert limpiar_texto_correo(texto) == "Buenas tardes, necesito 3 cajas de tomates para el jueves."


def test_quita_cita_y_firma_a_la_vez():
    texto = (
        "Perfecto, confirmo el pedido para el viernes.\n"
        "--\n"
        "Juan Pérez\n"
        "Frutería Juan\n\n"
        "El jue, 19 nov 2026 a las 09:00, Proveedor <proveedor@ejemplo.com> escribió:\n"
        "> Aquí tienes el presupuesto\n"
    )
    assert limpiar_texto_correo(texto) == "Perfecto, confirmo el pedido para el viernes."


def test_quita_lineas_citadas_sueltas_sin_cabecera():
    texto = (
        "Sí, por favor añade también 2 kg de naranjas.\n"
        "> pedido anterior: 3 cajas de tomates\n"
        "> entrega el jueves\n"
        "Gracias."
    )
    assert limpiar_texto_correo(texto) == "Sí, por favor añade también 2 kg de naranjas.\nGracias."


def test_correo_sin_citas_ni_firma_no_cambia():
    texto = "Quiero pedir 5 unidades de pan para mañana en la calle Mayor 3."
    assert limpiar_texto_correo(texto) == texto
