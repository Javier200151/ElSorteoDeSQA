import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
from bs4 import BeautifulSoup
import random
from collections import Counter

BASE_URL = "https://foro.squadalpha.es"
FORUM_URL = "https://foro.squadalpha.es/viewforum.php?f=18&sid=010f4a30f358286b9cd0298e71504ba8"

def obtener_lista_topics():
    response = requests.get(FORUM_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []
    for link in soup.select('a.topictitle'):
        topic_title = link.text.strip()
        topic_href = link['href']
        topic_url = f"{BASE_URL}/{topic_href}"
        topics.append((topic_title, topic_url))
    return topics

def cortar_string(contenido):
    inicio = "Se dispone"
    fin = "https://squadalpha.es/normativa/"
    pos_inicio = contenido.find(inicio)
    pos_fin = contenido.find(fin, pos_inicio)
    if pos_inicio != -1 and pos_fin != -1:
        trozo = contenido[pos_inicio:pos_fin + len(fin)]
        return trozo
    else:
        return "No se encontraron las frases especificadas en el contenido."

def extraer_orbat(url):
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        contenido_completo = soup.get_text()
        return cortar_string(contenido_completo)
    else:
        return "Error al obtener el contenido."
roles_importantes = {"Lider de escuadra", "Sargento", "HQ", "RTO", "JTAC", "Operador UAV", "Piloto", "Comandante", "Lider de peloton", "Lider", "Medico", "Sanitario", "Doctor", "Jefe de Equipo"}
roles_HQ = {"Sargento", "HQ"}

def quitar_tildes(texto):
    reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'ñ': 'n', 'Ñ': 'N'}
    for acentuada, simple in reemplazos.items():
        texto = texto.replace(acentuada, simple)
    return texto

def extraer_nombres(contenido):
    lineas = contenido.splitlines()
    nombres_importantes = []
    nombres_HQ = []
    for linea in lineas:
        linea_limpia = linea.strip()
        if ")-" in linea_limpia:
            rol, nombre = linea_limpia.split(")-")
            rol = quitar_tildes(rol.strip())
            nombre = nombre.strip()
            if any(quitar_tildes(rol_importante) in rol for rol_importante in roles_importantes):
                nombres_importantes.append(nombre)
                if any(quitar_tildes(rol_importante) in rol for rol_importante in roles_HQ):
                    nombres_HQ.append(nombre)
    return nombres_importantes, nombres_HQ

def extraer_nombres_filtrados(contenido, nombres_HQ):
    lineas = contenido.splitlines()
    nombres_filtrados = set()
    for linea in lineas:
        linea_limpia = linea.strip()
        if ")-" in linea_limpia:
            rol, nombre = linea_limpia.split(")-")
            rol = quitar_tildes(rol.strip())
            nombre = nombre.strip()
            if nombre and not any(quitar_tildes(rol_importante) in rol for rol_importante in roles_importantes):
                nombres_filtrados.add(nombre)
    return [i for i in nombres_filtrados if i not in nombres_HQ]

def procesar_analisis_y_sorteo(contenidos):
    todos_nombres_importantes = []
    nombres_HQ = []
    for contenido in contenidos[:3]:
        nombres_importantes, HQ = extraer_nombres(contenido)
        nombres_HQ += HQ
        todos_nombres_importantes.extend(nombres_importantes)
    contador_nombres_importantes = Counter(todos_nombres_importantes)
    nombres_filtrados_cuarto = extraer_nombres_filtrados(contenidos[3], nombres_HQ)
    resultado = []
    participantes = {}
    for nombre in nombres_filtrados_cuarto:
        conteo = 4 - contador_nombres_importantes.get(nombre, 0)
        resultado.append(f"{nombre}: {conteo} papeletas")
        participantes[nombre] = conteo
    return "\n".join(resultado), participantes

def iniciar_sorteo(participantes, premios, ruleta_text, tabla_ganadores):
    lista_papeletas = []
    for nombre, papeletas in participantes.items():
        lista_papeletas.extend([nombre] * papeletas)
    for premio in premios:
        if not lista_papeletas:
            break
        for _ in range(30):
            seleccionado = random.choice(lista_papeletas)
            ruleta_text.config(state="normal")
            ruleta_text.delete(1.0, tk.END)
            ruleta_text.insert(tk.END, f"Seleccionando...\n\n{seleccionado}")
            ruleta_text.config(state="disabled")
            ruleta_text.update_idletasks()
            ruleta_text.after(100)
        ganador = random.choice(lista_papeletas)
        lista_papeletas = [p for p in lista_papeletas if p != ganador]
        tabla_ganadores.insert("", "end", values=(premio, ganador))
        ruleta_text.delete(1.0, tk.END)
        ruleta_text.insert(tk.END, f"Rol de '{premio}' para: {ganador}\n")

def iniciar_interfaz():
    root = tk.Tk()
    root.title("La Ruleta de SQA")
    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10)
    frame_topics = tk.Frame(main_frame)
    frame_topics.grid(row=0, column=0, padx=10, pady=10, sticky="n")
    tk.Label(frame_topics, text="Selecciona los 3 Primeros Topics del Foro:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
    topics = obtener_lista_topics()
    seleccionados_1 = tk.StringVar()
    seleccionados_2 = tk.StringVar()
    seleccionados_3 = tk.StringVar()
    ttk.Label(frame_topics, text="Primera partida:").pack(anchor="w", pady=5)
    combo_1 = ttk.Combobox(frame_topics, values=[title for title, url in topics], state="readonly", textvariable=seleccionados_1)
    combo_1.pack(anchor="w", pady=5)
    ttk.Label(frame_topics, text="Segunda partida:").pack(anchor="w", pady=5)
    combo_2 = ttk.Combobox(frame_topics, values=[title for title, url in topics], state="readonly", textvariable=seleccionados_2)
    combo_2.pack(anchor="w", pady=5)
    ttk.Label(frame_topics, text="Tercera partida:").pack(anchor="w", pady=5)
    combo_3 = ttk.Combobox(frame_topics, values=[title for title, url in topics], state="readonly", textvariable=seleccionados_3)
    combo_3.pack(anchor="w", pady=5)
    tk.Label(frame_topics, text="Selecciona la partida a jugar:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
    cuarto_seleccionado = tk.StringVar()
    variables_cuarto = ttk.Combobox(frame_topics, values=[title for title, url in topics], state="readonly", textvariable=cuarto_seleccionado)
    variables_cuarto.pack(anchor="w", pady=5)
    cuarto_archivo_label = tk.Label(frame_topics, text="Partida actual: Ninguno", font=("Arial", 10, "italic"))
    cuarto_archivo_label.pack(anchor="w", pady=5)
    def analizar_y_mostrar():
        if not seleccionados_1.get() or not seleccionados_2.get() or not seleccionados_3.get() or not cuarto_seleccionado.get():
            messagebox.showerror("Error", "Debes seleccionar exactamente 3 topics y un cuarto archivo.")
            return
        seleccionados_urls = [
            next(url for title, url in topics if title == seleccionados_1.get()),
            next(url for title, url in topics if title == seleccionados_2.get()),
            next(url for title, url in topics if title == seleccionados_3.get())
        ]
        cuarto_url = next(url for title, url in topics if title == cuarto_seleccionado.get())
        contenidos = [extraer_orbat(url) for url in seleccionados_urls]
        cuarto_contenido = extraer_orbat(cuarto_url)
        contenidos.append(cuarto_contenido)
        resultado, participantes_data = procesar_analisis_y_sorteo(contenidos)
        resultado_text.delete(1.0, tk.END)
        resultado_text.insert(tk.END, resultado)
        global participantes
        participantes = participantes_data
        cuarto_archivo_label.config(text=f"Cuarto archivo seleccionado: {cuarto_seleccionado.get()}")
    tk.Button(frame_topics, text="Confirmar y Analizar", command=analizar_y_mostrar).pack(pady=10)
    frame_resultado = tk.Frame(main_frame)
    frame_resultado.grid(row=0, column=1, padx=10, pady=10, sticky="n")
    tk.Label(frame_resultado, text="Resultados del Análisis:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
    resultado_text = scrolledtext.ScrolledText(frame_resultado, width=40, height=20)
    resultado_text.pack(padx=10, pady=10)
    tk.Label(frame_resultado, text="Ruleta de Sorteo:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
    ruleta_text = scrolledtext.ScrolledText(frame_resultado, width=40, height=10, state="disabled")
    ruleta_text.pack(padx=10, pady=10)
    frame_sorteo = tk.Frame(main_frame)
    frame_sorteo.grid(row=0, column=2, padx=10, pady=10, sticky="n")
    tk.Label(frame_sorteo, text="Sorteo:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
    tk.Label(frame_sorteo, text="Premios:").pack(anchor="w", pady=5)
    premios_entry = tk.Entry(frame_sorteo, width=30)
    premios_entry.pack(anchor="w", pady=5)
    premios_list = []
    premios_text = tk.Text(frame_sorteo, width=30, height=10)
    premios_text.pack(anchor="w", pady=5)
    def agregar_premio():
        premio = premios_entry.get().strip()
        if premio:
            premios_list.append(premio)
            premios_text.insert(tk.END, f"{premio}\n")
            premios_entry.delete(0, tk.END)
    tk.Button(frame_sorteo, text="Añadir Premio", command=agregar_premio).pack(pady=5)
    tk.Label(frame_sorteo, text="Iniciar Sorteo:").pack(anchor="w", pady=5)
    tabla_ganadores = ttk.Treeview(frame_sorteo, columns=("Premio", "Ganador"), show="headings")
    tabla_ganadores.heading("Premio", text="Premio")
    tabla_ganadores.heading("Ganador", text="Ganador")
    tabla_ganadores.pack(pady=5)
    tk.Button(frame_sorteo, text="Iniciar Sorteo", command=lambda: iniciar_sorteo(participantes, premios_list, ruleta_text, tabla_ganadores)).pack(pady=5)
    root.mainloop()
iniciar_interfaz()
