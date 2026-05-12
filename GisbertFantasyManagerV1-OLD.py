import tkinter as tk
import json
from tkinter import messagebox, simpledialog, filedialog, ttk
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

class FantasyLeagueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gisbert's Fantasy League Manager")
        self.root.configure(bg="#f0f0f0")  # Fondo claro
        self.league_data = {}
        self.current_league = ""

        # Establecer el ícono de la ventana
        self.set_icon("icon.ico")  # Cambia "icon.png" por el nombre de tu archivo de ícono

        # Configuramos la interfaz gráfica
        self.setup_gui()

        # Configuramos atajos de teclado
        self.configure_shortcuts()

    def set_icon(self, icon_path):
        # Cargar el ícono usando PIL
        try:
            img = Image.open(icon_path)
            photo = ImageTk.PhotoImage(img)
            self.root.iconphoto(False, photo)
        except Exception as e:
            print(f"No se pudo cargar el ícono: {e}")

    def setup_gui(self):
        self.create_menu()
        self.create_main_frame()
        self.create_main_screen()

    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#333333", fg="#ffffff", activebackground="#555555", activeforeground="#ffffff")
        self.root.config(menu=menubar)
        
        # Menú de Liga
        league_menu = tk.Menu(menubar, tearoff=0, bg="#333333", fg="#ffffff", activebackground="#555555", activeforeground="#ffffff")
        league_menu.add_command(label="Crear Liga", command=self.create_league)
        league_menu.add_command(label="Cargar Liga", command=self.load_league)
        league_menu.add_command(label="Comandos Rápidos", command=self.show_shortcut_legend)
        menubar.add_cascade(label="Liga", menu=league_menu)

        # Menú de Historiales
        history_menu = tk.Menu(menubar, tearoff=0, bg="#333333", fg="#ffffff", activebackground="#555555", activeforeground="#ffffff")
        history_menu.add_command(label="Historial Completo", command=self.view_full_history)
        history_menu.add_command(label="Historial de Persona", command=self.view_person_history)
        menubar.add_cascade(label="Historiales", menu=history_menu)
        
        # Menú de Estadísticas
        #stats_menu = tk.Menu(menubar, tearoff=0, bg="#333333", fg="#ffffff", activebackground="#555555", activeforeground="#ffffff")
        #stats_menu.add_command(label="Gráfico de Saldos", command=self.plot_balances)
        #stats_menu.add_command(label="Estadísticas de Sobrepuja", command=self.plot_overbid_stats)
        #menubar.add_cascade(label="Estadísticas", menu=stats_menu)

    def on_closing(self):
        if self.current_league:
            self.save_league(self.current_league)
        self.root.destroy()

    def setup_gui(self):
        self.create_menu()
        self.create_main_frame()
        self.create_main_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Barra de estado con copyright y enlaces
        self.status_bar = tk.Frame(self.root, bg="#333333")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        copyright_text = "© 2024 Rannden-SHA | Visita mi sitio web: https://rannden-sha.github.io/"
        copyright_label = tk.Label(self.status_bar, text=copyright_text, bg="#333333", fg="#ffffff", anchor='w', padx=10)
        copyright_label.pack(side=tk.LEFT)

    def show_league_statistics(self, parent_frame):
        # Limpiar el frame
        self.clear_frame(parent_frame)

        # Recoger datos
        participants = list(self.league_data[self.current_league].keys())
        standings = [(p, data['saldo'] + data['valor_equipo']) for p, data in self.league_data[self.current_league].items()]
        max_bids = [(p, self.calculate_max_bid(data['saldo'], data['valor_equipo'])) for p, data in self.league_data[self.current_league].items()]
        overbids = [(p, self.calculate_overbid_percent(data['purchases'])) for p, data in self.league_data[self.current_league].items()]

        # Ordenar datos
        standings.sort(key=lambda x: x[1], reverse=True)
        max_bids.sort(key=lambda x: x[1], reverse=True)
        overbids.sort(key=lambda x: x[1], reverse=True)

        # Crear tabla de posiciones
        self.create_table(parent_frame, standings, "Tabla de Posiciones", ["Participante", "Valor Total (€)"])

        # Crear tabla de máximas pujas
        self.create_table(parent_frame, max_bids, "Máximas Pujas", ["Participante", "Máxima Puja (€)"])

        # Crear tabla de porcentajes de sobrepuja
        self.create_table(parent_frame, overbids, "Porcentajes de Sobrepuja", ["Participante", "Sobrepuja Promedio (%)"])

    def create_table(self, parent_frame, data, title, columns):
        frame = tk.Frame(parent_frame, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame, text=title, font=("Arial", 14), bg="#f0f0f0").pack(pady=5)

        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        for row in data:
            tree.insert("", "end", values=row)

        tree.pack(fill=tk.BOTH, expand=True)

    def display_image(self, parent_frame, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((300, 300), Image.LANCZOS)  # Cambia el tamaño de la imagen según sea necesario
            photo = ImageTk.PhotoImage(img)
        
            label = tk.Label(parent_frame, image=photo)
            label.image = photo  # Guardar una referencia de la imagen para evitar que sea recolectada por el garbage collector
            label.pack(pady=20)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")

    def create_main_screen(self):
        self.clear_frame(self.main_frame)

        if not self.current_league:
            welcome_label = tk.Label(self.main_frame, text="Bienvenido a Gisbert's Fantasy League Manager", font=("Arial", 24), bg="#f0f0f0", fg="#0000ff")
            welcome_label.pack(pady=20)
            info_label = tk.Label(self.main_frame, text="Cree o cargue una liga para comenzar.", font=("Arial", 16), bg="#f0f0f0")
            info_label.pack(pady=10)
            # Mostrar imagen
            image_path = "icon.ico"  # Cambia esto por la ruta de tu imagen
            self.display_image(self.main_frame, image_path)            
            return

        # Configura la vista de las tablas y las estadísticas
        left_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        for i, (participant, data) in enumerate(self.league_data[self.current_league].items()):
            frame = tk.Frame(left_frame, bg="#ffffff", bd=2, relief=tk.RAISED)
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")

            name_label = tk.Label(frame, text=participant, font=("Arial", 14), bg="#ffffff", fg="#0000ff")
            name_label.pack(pady=5)

            saldo_label = tk.Label(frame, text=f"Saldo: {self.format_number(data['saldo'])}€", font=("Arial", 12), bg="#ffffff", fg=self.get_color(data['saldo']))
            saldo_label.pack(pady=5)

            valor_label = tk.Label(frame, text=f"Valor del Equipo: {self.format_number(data['valor_equipo'])}€", font=("Arial", 12), bg="#ffffff")
            valor_label.pack(pady=5)

            max_bid_label = tk.Label(frame, text=f"Máxima Puja: {self.format_number(self.calculate_max_bid(data['saldo'], data['valor_equipo']))}€", font=("Arial", 12), bg="#ffffff")
            max_bid_label.pack(pady=5)

            overbid_percent = self.calculate_overbid_percent(data['purchases'])
            overbid_label = tk.Label(frame, text=f"Sobrepuja Promedio: {overbid_percent:.2f}%", font=("Arial", 12), bg="#ffffff")
            overbid_label.pack(pady=5)

            action_frame = tk.Frame(frame, bg="#ffffff")
            action_frame.pack(pady=5)

            tk.Button(action_frame, text="Compra", command=lambda p=participant: self.register_purchase(p), bg="#d0f0c0").grid(row=0, column=0, padx=5, pady=5)
            tk.Button(action_frame, text="Venta", command=lambda p=participant: self.register_sale(p), bg="#f0d0d0").grid(row=0, column=1, padx=5, pady=5)
            tk.Button(action_frame, text="Agregar Dinero", command=lambda p=participant: self.add_money(p)).grid(row=1, column=0, padx=5, pady=5)
            tk.Button(action_frame, text="Añadir Puntos", command=lambda p=participant: self.add_points(p)).grid(row=1, column=1, padx=5, pady=5)
            tk.Button(action_frame, text="Actualizar Valor Equipo", command=lambda p=participant: self.update_team_value(p)).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        quick_action_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        quick_action_frame.pack(pady=20)

        # Mostrar estadísticas en el lado derecho
        self.show_league_statistics(right_frame)


    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def configure_shortcuts(self):
        self.root.bind("<Control-n>", lambda event: self.create_league())
        self.root.bind("<Control-o>", lambda event: self.load_league())
        self.root.bind("<Control-s>", lambda event: self.save_league(self.current_league) if self.current_league else None)
        self.root.bind("<Control-d>", lambda event: self.add_money())
        self.root.bind("<Control-p>", lambda event: self.add_points())
        self.root.bind("<Control-b>", lambda event: self.register_purchase())
        self.root.bind("<Control-v>", lambda event: self.register_sale())
        self.root.bind("<Control-u>", lambda event: self.update_team_value())
        self.root.bind("<Control-h>", lambda event: self.view_full_history())
        self.root.bind("<Control-r>", lambda event: self.view_person_history())
        self.root.bind("<Control-N>", lambda event: self.create_league())
        self.root.bind("<Control-O>", lambda event: self.load_league())
        self.root.bind("<Control-S>", lambda event: self.save_league(self.current_league) if self.current_league else None)
        self.root.bind("<Control-D>", lambda event: self.add_money())
        self.root.bind("<Control-P>", lambda event: self.add_points())
        self.root.bind("<Control-B>", lambda event: self.register_purchase())
        self.root.bind("<Control-V>", lambda event: self.register_sale())
        self.root.bind("<Control-U>", lambda event: self.update_team_value())
        self.root.bind("<Control-H>", lambda event: self.view_full_history())
        self.root.bind("<Control-R>", lambda event: self.view_person_history())

    def show_shortcut_legend(self):
        legend_window = tk.Toplevel(self.root)
        legend_window.title("Leyenda de Atajos de Teclado")
        legend_window.geometry("300x250")
        
        tk.Label(legend_window, text="Leyenda de Atajos de Teclado", font=("Arial", 14)).pack(pady=10)
        
        shortcuts = [
            ("Ctrl + D", "Añadir Dinero"),
            ("Ctrl + P", "Añadir Puntos"),
            ("Ctrl + B", "Registrar Compra"),
            ("Ctrl + V", "Registrar Venta"),
            ("Ctrl + U", "Actualizar Valor del Equipo"),
            ("Ctrl + H", "Ver Historial Completo"),
            ("Ctrl + R", "Ver Historial de Persona"),
            ("Ctrl + S", "Mostrar Leyenda de Atajos")
        ]
        
        for key, action in shortcuts:
            tk.Label(legend_window, text=f"{key}: {action}", font=("Arial", 12)).pack(anchor="w", padx=10)

        # Añadir aviso de copyright
        copyright_text = "© 2024 Rannden-SHA | Visita mi sitio web: www.tusitio.com"
        tk.Label(legend_window, text=copyright_text, bg="#f0f0f0", fg="#000000", anchor='w', padx=10, font=("Arial", 10)).pack(side=tk.BOTTOM, fill=tk.X, pady=10)


    def create_league(self):
        league_name = simpledialog.askstring("Crear Liga", "Nombre de la Liga:")
        if league_name:
            participants = simpledialog.askstring("Crear Liga", "Nombres de los participantes (separados por comas):")
            if participants:
                participant_list = [name.strip() for name in participants.split(',')]
                self.league_data[league_name] = {name: {'saldo': 0, 'historial': [], 'valor_equipo': 0, 'purchases': []} for name in participant_list}
                self.save_league(league_name)
                self.current_league = league_name
                self.root.title(f"Gisbert's Fantasy League Manager - {league_name}")  # Actualizar el título
                messagebox.showinfo("Liga Creada", f"Liga '{league_name}' creada con éxito.")
                self.create_main_screen()

    
    def load_league(self):
        file_path = filedialog.askopenfilename(title="Cargar Liga", filetypes=[("JSON files", "*.json")])
        if file_path:
            league_name = os.path.basename(file_path).replace('.json', '')
            with open(file_path, 'r') as f:
                self.league_data[league_name] = json.load(f)
            self.current_league = league_name
            self.root.title(f"Gisbert's Fantasy League Manager - {league_name}")  # Actualizar el título
            messagebox.showinfo("Liga Cargada", f"Liga '{league_name}' cargada con éxito.")
            self.create_main_screen()

    
    def save_league(self, league_name):
        with open(f"{league_name}.json", 'w') as f:
            json.dump(self.league_data[league_name], f, indent=4)
    
    def register_sale(self, participant=None):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        if participant is None:
            participant = simpledialog.askstring("Registrar Venta", "¿Quién vende?")
        
        player = simpledialog.askstring("Registrar Venta", "Nombre del jugador:")
        price = simpledialog.askfloat("Registrar Venta", "Precio de venta:")
        if participant and player and price is not None:
            prev_saldo = self.league_data[self.current_league][participant]['saldo']
            self.league_data[self.current_league][participant]['saldo'] += price
            self.league_data[self.current_league][participant]['historial'].append(f"Venta: {player}, Precio: {price}€, Saldo previo: {self.format_number(prev_saldo)}€, Saldo actual: {self.format_number(self.league_data[self.current_league][participant]['saldo'])}€")
            self.save_league(self.current_league)
            messagebox.showinfo("Venta Registrada", f"Venta de {player} por {participant} registrada con éxito.")
            self.create_main_screen()

    def register_purchase(self, participant=None):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        if participant is None:
            participant = simpledialog.askstring("Registrar Compra", "¿Quién compra?")
        
        player = simpledialog.askstring("Registrar Compra", "Nombre del jugador:")
        market_value = simpledialog.askfloat("Registrar Compra", "Valor de mercado del jugador:")
        purchase_price = simpledialog.askfloat("Registrar Compra", "Precio de compra:")
        if participant and player and market_value is not None and purchase_price is not None:
            prev_saldo = self.league_data[self.current_league][participant]['saldo']
            self.league_data[self.current_league][participant]['saldo'] -= purchase_price
            self.league_data[self.current_league][participant]['historial'].append(f"Compra: {player}, Precio: {purchase_price}€, Valor de mercado: {market_value}€, Saldo previo: {self.format_number(prev_saldo)}€, Saldo actual: {self.format_number(self.league_data[self.current_league][participant]['saldo'])}€")
            self.league_data[self.current_league][participant]['purchases'].append(purchase_price / market_value * 100 - 100)  # Registro del porcentaje de sobrepuja
            self.save_league(self.current_league)
            messagebox.showinfo("Compra Registrada", f"Compra de {player} por {participant} registrada con éxito.")
            self.create_main_screen()

    def add_money(self, participant=None):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        if participant is None:
            participant = simpledialog.askstring("Agregar Dinero", "¿A quién se le añade dinero?")
        
        amount = simpledialog.askfloat("Agregar Dinero", "Cantidad de dinero a añadir:")
        if participant and amount is not None:
            prev_saldo = self.league_data[self.current_league][participant]['saldo']
            self.league_data[self.current_league][participant]['saldo'] += amount
            self.league_data[self.current_league][participant]['historial'].append(f"Adición de dinero: {amount}€, Saldo previo: {self.format_number(prev_saldo)}€, Saldo actual: {self.format_number(self.league_data[self.current_league][participant]['saldo'])}€")
            self.save_league(self.current_league)
            messagebox.showinfo("Dinero Añadido", f"{amount}€ añadidos a {participant}.")
            self.create_main_screen()

    def add_points(self, participant=None):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        if participant is None:
            participant = simpledialog.askstring("Añadir Puntos", "¿A quién se le añaden puntos?")
        
        points = simpledialog.askinteger("Añadir Puntos", "Puntos obtenidos:")
        if participant and points is not None:
            amount = points * 100000
            prev_saldo = self.league_data[self.current_league][participant]['saldo']
            self.league_data[self.current_league][participant]['saldo'] += amount
            self.league_data[self.current_league][participant]['historial'].append(f"Adición de puntos: {points} puntos ({amount}€), Saldo previo: {self.format_number(prev_saldo)}€, Saldo actual: {self.format_number(self.league_data[self.current_league][participant]['saldo'])}€")
            self.save_league(self.current_league)
            messagebox.showinfo("Puntos Añadidos", f"{points} puntos añadidos a {participant} ({amount}€).")
            self.create_main_screen()

    def update_team_value(self, participant=None):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        if participant is None:
            participant = simpledialog.askstring("Actualizar Valor del Equipo", "¿A quién se le actualiza el valor del equipo?")
        
        new_value = simpledialog.askfloat("Actualizar Valor del Equipo", "Nuevo valor del equipo:")
        if participant and new_value is not None:
            self.league_data[self.current_league][participant]['valor_equipo'] = new_value
            prev_value = self.league_data[self.current_league][participant]['valor_equipo']
            self.league_data[self.current_league][participant]['historial'].append(f"Actualización del valor del equipo: de {self.format_number(prev_value)}€ a {self.format_number(new_value)}€")
            self.save_league(self.current_league)
            messagebox.showinfo("Valor del Equipo Actualizado", f"Valor del equipo de {participant} actualizado a {new_value}€.")
            self.create_main_screen()
    

    def view_full_history(self):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        full_history = []
        for name, data in self.league_data[self.current_league].items():
            for record in data['historial']:
                full_history.append([name, record])
        self.show_history_table(full_history, "Historial Completo")

    def view_person_history(self, participant=None):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        if participant is None:
            participant = simpledialog.askstring("Ver Historial de Persona", "Nombre de la persona:")
        
        if participant and participant in self.league_data[self.current_league]:
            person_history = [[participant, record] for record in self.league_data[self.current_league][participant]['historial']]
            self.show_history_table(person_history, f"Historial de {participant}")
    
    def show_history_table(self, data, title):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.configure(bg="#f0f0f0")

        frame = tk.Frame(window, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Añadir campo de búsqueda
        search_frame = tk.Frame(frame, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Buscar:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Buscar", command=lambda: self.update_history_table(tree, data)).pack(side=tk.LEFT)
        
        # Configurar tabla
        cols = ('Participante', 'Registro')
        tree = ttk.Treeview(frame, columns=cols, show='headings')
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')
        
        # Mostrar todos los datos inicialmente
        self.update_history_table(tree, data)
        
        tree.pack(fill=tk.BOTH, expand=True)

        # Añadir aviso de copyright
        copyright_text = "© 2024 Rannden-SHA | Visita mi sitio web: https://rannden-sha.github.io/"
        tk.Label(window, text=copyright_text, bg="#f0f0f0", fg="#000000", anchor='w', padx=10, font=("Arial", 10)).pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    
    def update_history_table(self, tree, data):
        # Obtener término de búsqueda
        search_term = self.search_entry.get().lower()
        
        # Limpiar el árbol de vista
        tree.delete(*tree.get_children())
        
        # Filtrar datos
        filtered_data = [row for row in data if search_term in row[1].lower()]
        
        # Insertar datos filtrados en la tabla
        for row in filtered_data:
            tree.insert("", "end", values=row)
    
    def format_number(self, number):
        return "{:,}".format(int(number)).replace(",", ".")

    def get_color(self, value):
        if value < 0:
            return "#ff0000"  # Rojo para números negativos
        elif value > 0:
            return "#00ff00"  # Verde para números positivos
        return "#000000"  # Negro para cero

    def calculate_max_bid(self, saldo, valor_equipo):
        return saldo + 0.2 * valor_equipo

    def calculate_overbid_percent(self, purchases):
        if not purchases:
            return 0
        return sum(purchases) / len(purchases)

    def plot_balances(self):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return
        
        names = list(self.league_data[self.current_league].keys())
        balances = [self.league_data[self.current_league][name]['saldo'] for name in names]

        fig, ax = plt.subplots()
        ax.bar(names, balances, color='skyblue')
        ax.set_xlabel('Participantes')
        ax.set_ylabel('Saldo (€)')
        ax.set_title('Saldos de los Participantes')
        plt.xticks(rotation=45)
        
        # Mostrar el gráfico en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def plot_overbid_stats(self):
        if not self.current_league:
            messagebox.showwarning("Advertencia", "Por favor, cargue una liga primero.")
            return

        # Recoger datos para la gráfica
        ranges = [0, 5000, 10000, 20000, 30000, 50000, 100000]
        bins = [0] * (len(ranges) - 1)
        for data in self.league_data[self.current_league].values():
            for purchase in data['purchases']:
                for i in range(len(ranges) - 1):
                    if ranges[i] <= purchase <= ranges[i + 1]:
                        bins[i] += 1
                        break

        fig, ax = plt.subplots()
        ax.bar([f'{ranges[i]}-{ranges[i + 1]}' for i in range(len(bins))], bins, color='salmon')
        ax.set_xlabel('Rango de Precios')
        ax.set_ylabel('Cantidad de Compras')
        ax.set_title('Estadísticas de Sobrepuja')
        ax.tick_params(axis='x', rotation=45)

        # Mostrar el gráfico en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

def main():
    root = tk.Tk()
    app = FantasyLeagueApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
