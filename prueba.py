import json
import PySimpleGUI as sg
from datetime import datetime

def cargar_base_datos():
    try:
        with open('base_datos.json', 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

def cargar_historial():
    try:
        with open('historial.json', 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

def guardar_historial(entrega):
    historial = cargar_historial()
    historial.append(entrega)
    with open('historial.json', 'w') as archivo:
        json.dump(historial, archivo, indent=2)

def guardar_base_datos(base_datos):
    with open('base_datos.json', 'w') as archivo:
        json.dump(base_datos, archivo, indent=2)

def validar_campos_vacios(values, campos):
    for campo in campos:
        if values[campo] == '':
            sg.popup_error(f"¡Error! El campo '{campo}' no puede estar vacío.")
            return False
    return True

def agregar_insumo_nueva_ventana():
    layout = [
        [sg.Text("Nombre del insumo:"), sg.InputText(key='-NOMBRE-')],
        [sg.Text("Cantidad:"), sg.InputText(key='-CANTIDAD-')],
        [sg.Button("Agregar insumo"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Agregar Insumo", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancelar":
            window.close()
            return None

        if event == "Agregar insumo":
            nombre = values['-NOMBRE-']
            cantidad = values['-CANTIDAD-']

            if not validar_campos_vacios(values, ['-NOMBRE-', '-CANTIDAD-']):
                continue

            window.close()
            return nombre, int(cantidad)

def realizar_entrega_nueva_ventana():
    layout = [
        [sg.Text("Nombre del insumo:"), sg.InputText(key='-NOMBRE-')],
        [sg.Text("Cantidad:"), sg.InputText(key='-CANTIDAD-')],
        [sg.Text("Destinatario:"), sg.InputText(key='-DESTINATARIO-')],
        [sg.Text("Fecha (DD/MM/YYYY):"), sg.InputText(key='-FECHA-')],
        [sg.Button("Realizar entrega"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Realizar Entrega", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancelar":
            window.close()
            return None

        if event == "Realizar entrega":
            nombre = values['-NOMBRE-']
            cantidad = values['-CANTIDAD-']
            destinatario = values['-DESTINATARIO-']
            fecha = values['-FECHA-']

            if not validar_campos_vacios(values, ['-NOMBRE-', '-CANTIDAD-', '-DESTINATARIO-', '-FECHA-']):
                continue

            try:
                fecha_entrega = datetime.strptime(fecha, '%d/%m/%Y')
            except ValueError:
                sg.popup_error("¡Error! El formato de fecha ingresado es incorrecto. Utilice DD/MM/YYYY.")
                continue

            window.close()
            return nombre, int(cantidad), destinatario, fecha_entrega

def agregar_insumo(window):
    nombre_cantidad = agregar_insumo_nueva_ventana()

    if nombre_cantidad is not None:
        nombre, cantidad = nombre_cantidad
        base_datos = cargar_base_datos()

        if nombre in base_datos:
            base_datos[nombre] += cantidad
        else:
            base_datos[nombre] = cantidad

        guardar_base_datos(base_datos)
        window['-OUTPUT-'].update(f"Insumo {nombre} agregado correctamente.")

def realizar_entrega(window):
    entrega_info = realizar_entrega_nueva_ventana()

    if entrega_info is not None:
        nombre, cantidad, destinatario, fecha_entrega = entrega_info
        base_datos = cargar_base_datos()

        if nombre in base_datos and base_datos[nombre] >= cantidad:
            base_datos[nombre] -= cantidad
            guardar_base_datos(base_datos)
            entrega = {'Nombre': nombre, 'Cantidad': cantidad, 'Destinatario': destinatario, 'Fecha': fecha_entrega.strftime('%d/%m/%Y')}
            guardar_historial(entrega)
            window['-OUTPUT-'].update(f"Entrega de {cantidad} unidades de {nombre} a {destinatario} realizada el {fecha_entrega.strftime('%d/%m/%Y')} correctamente.")
        else:
            window['-OUTPUT-'].update(f"No hay suficientes unidades de {nombre} en el stock para realizar la entrega.")

def mostrar_stock(window):
    base_datos = cargar_base_datos()

    if not base_datos:
        window['-OUTPUT-'].update("La base de datos de stock está vacía.")
    else:
        stock_actual = "\n".join([f"{insumo}: {cantidad}" for insumo, cantidad in base_datos.items()])
        window['-OUTPUT-'].update(f"Stock actual:\n{stock_actual}")

def mostrar_historial():
    historial = cargar_historial()

    if not historial:
        sg.popup("El historial de entregas está vacío.")
    else:
        historial_texto = "\n".join([f"{entrega['Nombre']} - Cantidad: {entrega['Cantidad']}, Destinatario: {entrega['Destinatario']}, Fecha: {entrega['Fecha']}" for entrega in historial])
        sg.popup_scrolled("Historial de Entregas", historial_texto)

def buscar_insumo():
    layout = [
        [sg.Text("Nombre del insumo:"), sg.InputText(key='-BUSCAR-NOMBRE-')],
        [sg.Button("Buscar"), sg.Button("Cancelar")]
    ]

    window = sg.Window("Buscar Insumo", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancelar":
            window.close()
            return None

        if event == "Buscar":
            nombre_buscado = values['-BUSCAR-NOMBRE-']
            window.close()
            return nombre_buscado

def modificar_insumo(window, values):
    nombre_buscado = values['-BUSCAR-NOMBRE-']

    if not nombre_buscado:
        return

    base_datos = cargar_base_datos()

    resultados_coincidentes = [insumo for insumo in base_datos.keys() if nombre_buscado.lower() in insumo.lower()]

    if not resultados_coincidentes:
        window['-OUTPUT-'].update(f"No se encontraron insumos que coincidan con: {nombre_buscado}")
        return

    layout = [
        [sg.Text("Selecciona el insumo a modificar:")],
        [sg.Listbox(resultados_coincidentes, size=(30, len(resultados_coincidentes)), key='-LISTA-')],
        [sg.Button("Seleccionar"), sg.Button("Cancelar")]
    ]

    sub_window = sg.Window("Resultados de la Búsqueda", layout)

    while True:
        event, values = sub_window.read()

        if event == sg.WIN_CLOSED or event == "Cancelar":
            sub_window.close()
            return

        if event == "Seleccionar":
            seleccion = values['-LISTA-']

            if not seleccion:
                sg.popup_error("¡Error! Debes seleccionar un insumo.")
                continue

            sub_window.close()
            insumo_seleccionado = seleccion[0]
            modificar_cantidad_insumo(window, base_datos, insumo_seleccionado)

def modificar_cantidad_insumo(window, base_datos, insumo_seleccionado):
    layout = [
        [sg.Text(f"Modificar insumo: {insumo_seleccionado}")],
        [sg.Text("Nueva cantidad:"), sg.InputText(key='-NUEVA-CANTIDAD-')],
        [sg.Button("Guardar"), sg.Button("Cancelar")]
    ]

    sub_window = sg.Window("Modificar Insumo", layout)

    while True:
        event, values = sub_window.read()

        if event == sg.WIN_CLOSED or event == "Cancelar":
            sub_window.close()
            return

        if event == "Guardar":
            if values['-NUEVA-CANTIDAD-'] == '':
                sg.popup_error("¡Error! El campo 'Nueva cantidad' no puede estar vacío.")
                continue

            nueva_cantidad = int(values['-NUEVA-CANTIDAD-'])
            base_datos[insumo_seleccionado] = nueva_cantidad
            guardar_base_datos(base_datos)
            window['-OUTPUT-'].update(f"Insumo {insumo_seleccionado} modificado correctamente.")
            sub_window.close()
            return

    sub_window.close()

def main():
    sg.theme('DarkGrey1')  # Cambiar el tema para un aspecto más atractivo

    layout = [
        [sg.Text("Sistema de Gestión de Stock y Entregas", font=("Helvetica", 16))],
        [sg.Button("Agregar Insumo", size=(20, 2)), sg.Button("Realizar Entrega", size=(20, 2)), sg.Button("Mostrar Stock", size=(20, 2)), sg.Button("Historial de Entregas", size=(20, 2)), sg.Button("Buscar y Modificar", size=(20, 2))],
        [sg.Text(size=(40, 5), key='-OUTPUT-')],
        [sg.Button("Salir", size=(20, 2))]
    ]

    window = sg.Window("Menú Principal", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Salir":
            break
        elif event == "Agregar Insumo":
            agregar_insumo(window)
        elif event == "Realizar Entrega":
            realizar_entrega(window)
        elif event == "Mostrar Stock":
            mostrar_stock(window)
        elif event == "Historial de Entregas":
            mostrar_historial()
        elif event == "Buscar y Modificar":
            nombre = buscar_insumo()
            if nombre:
                modificar_insumo(window, {'-BUSCAR-NOMBRE-': nombre})

    window.close()

if __name__ == "__main__":
    main()
