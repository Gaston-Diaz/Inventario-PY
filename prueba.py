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
        [sg.Text(size=(40, 5), key='-OUTPUT-')],
        [sg.Button("Agregar insumo"), sg.Button("Cancelar",button_color=('white', 'red'))],
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
        [sg.Column([
                    [sg.Text("Nombre del insumo:"), sg.InputText(key='-NOMBRE-')],
                    [sg.Text("Cantidad:"), sg.InputText(key='-CANTIDAD-')],
                    [sg.Text("Destinatario:"), sg.InputText(key='-DESTINATARIO-')],
                    [sg.Text("Fecha (DD/MM/YYYY):"), sg.InputText(key='-FECHA-')],
                    ], vertical_alignment='center')],
        [sg.Text(size=(40, 5), key='-OUTPUT-')],
        [sg.Button("Buscar Insumo"), sg.Button("Realizar entrega"), sg.Button("Cancelar", button_color=('white', 'red'))],
    ]

    window = sg.Window("Realizar Entrega", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancelar":
            window.close()
            return None

        if event == "Buscar Insumo":
            nombre_buscado = values['-NOMBRE-']
            base_datos = cargar_base_datos()

            resultados_coincidentes = [insumo for insumo in base_datos.keys() if nombre_buscado.lower() in insumo.lower()]

            if not resultados_coincidentes:
                sg.popup_error(f"No se encontraron insumos que coincidan con: {nombre_buscado}")
            else:
                layout_resultados = [
                    [sg.Text("Selecciona el insumo:")],
                    [sg.Listbox(resultados_coincidentes, size=(50, len(resultados_coincidentes)) ,key='-LISTA-')], #
                    [sg.Text(size=(40, 5), key='-OUTPUT-')],
                    [sg.Button("Seleccionar")]
                ]

                sub_window_resultados = sg.Window("Resultados de la Búsqueda", layout_resultados)

                while True:
                    event_resultados, values_resultados = sub_window_resultados.read()

                    if event_resultados == sg.WIN_CLOSED:
                        sub_window_resultados.close()
                        break

                    if event_resultados == "Seleccionar":
                        seleccion = values_resultados['-LISTA-']

                        if not seleccion:
                            sg.popup_error("¡Error! Debes seleccionar un insumo.")
                            continue

                        sub_window_resultados.close()
                        window['-NOMBRE-'].update(seleccion[0])
                        break

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

def mostrar_stock_nueva_ventana(filtro_producto=None):
    base_datos = cargar_base_datos()

    if not base_datos:
        sg.popup("La base de datos de stock está vacía.")
    else:
        if filtro_producto:
            # Usa una comprensión de lista para filtrar según el filtro de producto proporcionado
            base_datos_filtrada = {insumo: cantidad for insumo, cantidad in base_datos.items() if filtro_producto.lower() in insumo.lower()}
        else:
            base_datos_filtrada = base_datos

        if not base_datos_filtrada:
            sg.popup(f"No hay insumos para el producto '{filtro_producto}'.")
        else:
            layout = [
                [sg.Text("Stock actual:")],
                [sg.Multiline("\n".join([f"{insumo}: {cantidad}" for insumo, cantidad in base_datos_filtrada.items()]), size=(40, 10), key='-STOCK-')],
                [sg.Text(size=(40, 5), key='-OUTPUT-')],
                [sg.Button("Copiar"), sg.Button("Cerrar",button_color=('white', 'red'))]
            ]

            window_stock = sg.Window("Stock Actual", layout)

            while True:
                event_stock, values_stock = window_stock.read()

                if event_stock == sg.WIN_CLOSED or event_stock == "Cerrar":
                    window_stock.close()
                    break

                if event_stock == "Copiar":
                    sg.popup("¡Datos copiados al portapapeles!")
                    sg.clipboard_set("\n".join([f"{insumo}: {cantidad}" for insumo, cantidad in base_datos_filtrada.items()]))

def mostrar_historial_nueva_ventana(filtro_producto=None):
    historial = cargar_historial()

    if not historial:
        sg.popup("El historial de entregas está vacío.")
    else:
        if filtro_producto:
            historial_filtrado = [entrega for entrega in historial if filtro_producto.lower() in entrega['Nombre'].lower()]
        else:
            historial_filtrado = historial

        if not historial_filtrado:
            sg.popup(f"No hay entregas para el producto '{filtro_producto}'.")
        else:
            layout = [
                [sg.Text("Historial de Entregas:")],
                [sg.Multiline("\n".join([f"{entrega['Nombre']} - Cantidad: {entrega['Cantidad']}, Destinatario: {entrega['Destinatario']}, Fecha: {entrega['Fecha']}" for entrega in historial_filtrado]), size=(60, 15), key='-HISTORIAL-')],
                [sg.Text(size=(40, 5), key='-OUTPUT-')],
                [sg.Button("Copiar"), sg.Button("Cerrar", button_color=('white', 'red'))]
            ]

            window_historial = sg.Window("Historial de Entregas", layout)

            while True:
                event_historial, values_historial = window_historial.read()

                if event_historial == sg.WIN_CLOSED or event_historial == "Cerrar":
                    window_historial.close()
                    break

                if event_historial == "Copiar":
                    sg.popup("¡Datos copiados al portapapeles!")
                    sg.clipboard_set("\n".join([f"{entrega['Nombre']} - Cantidad: {entrega['Cantidad']}, Destinatario: {entrega['Destinatario']}, Fecha: {entrega['Fecha']}" for entrega in historial_filtrado]))


def mostrar_stock(window):
    filtro_producto = sg.popup_get_text("Filtrar por producto (dejar en blanco para mostrar todo):", title="Filtrar Stock")
    mostrar_stock_nueva_ventana(filtro_producto)

def mostrar_historial():
    filtro_producto = sg.popup_get_text("Filtrar por producto (dejar en blanco para mostrar todo):", title="Filtrar Historial")
    mostrar_historial_nueva_ventana(filtro_producto)

#    historial = cargar_historial()

#    if not historial:
#        sg.popup("El historial de entregas está vacío.")
#    else:
#        historial_texto = "\n".join([f"{entrega['Nombre']} - Cantidad: {entrega['Cantidad']}, Destinatario: {entrega['Destinatario']}, Fecha: {entrega['Fecha']}" for entrega in historial])
#        sg.popup_scrolled("Historial de Entregas", historial_texto)

def buscar_insumo():
    layout = [
        [sg.Text("Nombre del insumo:"), sg.InputText(key='-BUSCAR-NOMBRE-')],
        [sg.Text(size=(40, 5), key='-OUTPUT-')],
        [sg.Button("Buscar"), sg.Button("Cancelar", button_color=('white', 'red'))] 
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
        [sg.Listbox(resultados_coincidentes, size=(50, len(resultados_coincidentes)), key='-LISTA-')], #len(resultados_coincidentes)
        [sg.Text(size=(40, 5), key='-OUTPUT-')],
        [sg.Button("Seleccionar"), sg.Button("Cancelar", button_color=('white', 'red'))]
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
        [sg.Text(size=(40, 5), key='-OUTPUT-')],
        [sg.Button("Guardar"), sg.Button("Cancelar", button_color=('white', 'red'))]
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
    sg.theme('DarkTeal7')  # Cambiar el tema para un aspecto más atractivo
    layout = [
        [sg.Text("Sistema de Gestión de Stock y Entregas", font=("Helvetica", 20))],
        [sg.Image(filename='C:/Users/Usuario/Desktop/Inv-Py/download2.png')],
        [
            sg.Button(image_filename='C:/Users/Usuario/Desktop/Inv-Py/icons/agregarICO.png', image_size=(60, 60), border_width=0, key="Agregar Insumo"),
            sg.Text("Agregar Insumo", size=(17, 1)),
            sg.Button(image_filename='C:/Users/Usuario/Desktop/Inv-Py/icons/icoEntrega.png', image_size=(60, 60), border_width=0, key="Realizar Entrega"),
            sg.Text("Realizar Entrega", size=(17, 1)),
            sg.Button(image_filename='C:/Users/Usuario/Desktop/Inv-Py/icons/icoStock.png', image_size=(60, 60), border_width=0, key="Mostrar Stock"),
            sg.Text("Mostrar Stock", size=(17, 1)),
            sg.Button(image_filename='C:/Users/Usuario/Desktop/Inv-Py/icons/historial.png', image_size=(60, 60), border_width=0, key="Historial de Entregas"),
            sg.Text("Historial de Entregas", size=(17, 1)),
            sg.Button(image_filename='C:/Users/Usuario/Desktop/Inv-Py/icons/icoEditar.png', image_size=(60, 60), border_width=0, key="Buscar y Modificar"),
            sg.Text("Buscar y Modificar", size=(17, 1)),
        ],

        [sg.Text(size=(40, 5), key='-OUTPUT-')],

        [sg.Button("Salir", size=(20, 2), button_color=('white', 'red'))],

        #[sg.Button(image_filename='C:/Users/Usuario/Desktop/Inv-Py/icoEntrega.png', image_size=(60, 60), border_width=0),
        # sg.Text("texto_boton", size=(30, 1))],
    ]

    window = sg.Window("Menú Principal", layout, element_justification='center',size=(1200, 800))

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
