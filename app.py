import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from main import GmlReader
import re

show_dzialki = True
show_budynki = True

DEFAULT_PATH = r'C:\uni\5sem\kataster\proj2\dane\Zbiór danych GML ZSK 2025.gml.txt'

class GmlViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Przeglądarka GML")
        self.root.geometry("1000x700")
        
        self.reader = None
        self.canvas_objects = {}
        self.current_path = DEFAULT_PATH
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.global_min_x = 0
        self.global_max_x = 0
        self.global_min_y = 0
        self.global_max_y = 0
        
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.import_btn = ttk.Button(control_frame, text="Wczytaj dane", command=self.import_gml)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        self.browse_btn = ttk.Button(control_frame, text="Wybierz źródło danych", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_zoom_btn = ttk.Button(control_frame, text="Reset widoku", command=self.reset_zoom)
        self.reset_zoom_btn.pack(side=tk.LEFT, padx=5)

        self.var_dzialki = tk.BooleanVar(value=True)
        self.var_budynki = tk.BooleanVar(value=True)
        self.var_punkty = tk.BooleanVar(value=True)
        self.var_kontury = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(control_frame, text="Działki", variable=self.var_dzialki, 
                       command=self.update_display).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Budynki", variable=self.var_budynki,
                       command=self.update_display).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Punkty graniczne", variable=self.var_punkty,
                       command=self.update_display).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Kontury użytków", variable=self.var_kontury,
                       command=self.update_display).pack(side=tk.LEFT, padx=5)

        main_frame = ttk.Frame(root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        info_frame = ttk.LabelFrame(main_frame, text="Informacje o obiekcie", padding="10")
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        self.info_text = tk.Text(info_frame, width=30, height=20, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.insert("1.0", "Kliknij na obiekt aby zobaczyć szczegóły")
        self.info_text.config(state=tk.DISABLED)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', bd=2, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-3>", self.on_drag_start)
        self.canvas.bind("<B3-Motion>", self.on_drag_motion)
        
        footer_frame = ttk.Frame(root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=0)
        
        footer_label = ttk.Label(
            footer_frame, 
            text="Jakub Fedorowicz 331913, Weronika Klimkowicz 331916, Kazimierz Dym 326460, Julia Chmielewska 331912",
            font=('Arial', 9),
            foreground='gray'
        )
        footer_label.pack(side=tk.RIGHT)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Wybierz plik GML",
            filetypes=[("Pliki GML", "*.gml *.txt"), ("Wszystkie pliki", "*.*")],
            initialdir=r"C:\uni\5sem\kataster\proj2\dane"
        )
        if filename:
            self.current_path = filename
            self.status_label.config(text=f"Wybrano: {filename.split('/')[-1]}")
    
    def reset_zoom(self):
        """Przywrócenie oryginalnego widoku"""
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        if self.reader is not None:
            self.update_display(recalculate_bounds=False)
        
    def import_gml(self):
        try:
            self.root.update()
            
            self.reader = GmlReader(self.current_path)
            
            self.update_display(recalculate_bounds=True)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać pliku: {str(e)}")
            self.status_label.config(text="Błąd importu")
    
    def update_display(self, recalculate_bounds=False):
        if self.reader is None:
            return
        
        self.canvas.delete("all")
        
        global show_dzialki, show_budynki
        show_dzialki = self.var_dzialki.get()
        show_budynki = self.var_budynki.get()
        show_punkty = self.var_punkty.get()
        show_kontury = self.var_kontury.get()
        
        if recalculate_bounds:
            all_coords = []
            for member in self.reader.members:
                if member.geometry_type == 'Polygon' and member.geometry:
                    coords = self.parse_coordinates(member.geometry)
                    if coords:
                        all_coords.extend(coords)
            
            if all_coords:
                xs = [c[0] for c in all_coords]
                ys = [c[1] for c in all_coords]

                margin = 200
                self.global_min_x, self.global_max_x = min(xs) - margin, max(xs) + margin
                self.global_min_y, self.global_max_y = min(ys) - margin, max(ys) + margin
        

        dzialki_to_draw = []
        budynki_to_draw = []
        punkty_to_draw = []
        kontury_to_draw = []
        seen_contours = set()
        
        for member in self.reader.members:
            if member.geometry_type == 'Polygon' and member.geometry:
                if member.feature_type == 'egb:EGB_DzialkaEwidencyjna' and show_dzialki:
                    dzialki_to_draw.append(member)
                elif member.feature_type == 'egb:EGB_Budynek' and show_budynki:
                    budynki_to_draw.append(member)
                elif member.feature_type == 'egb:EGB_KonturKlasyfikacyjny' and show_kontury:
                    if member.gml_id and member.gml_id not in seen_contours:
                        kontury_to_draw.append(member)
                        seen_contours.add(member.gml_id)
            elif member.geometry_type == 'Point' and member.geometry:
                if member.feature_type == 'egb:EGB_PunktGraniczny' and show_punkty:
                    punkty_to_draw.append(member)
        
        min_x, max_x = self.global_min_x, self.global_max_x
        min_y, max_y = self.global_min_y, self.global_max_y
        
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 980
        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 600
        
        margin = 50
        scale_x = (canvas_width - 2 * margin) / (max_x - min_x) if max_x != min_x else 1
        scale_y = (canvas_height - 2 * margin) / (max_y - min_y) if max_y != min_y else 1
        base_scale = min(scale_x, scale_y)
        scale = base_scale * self.zoom_level
        
        def transform(x, y):
            canvas_x = (y - min_y) * scale + margin + self.offset_x
            canvas_y = (max_x - x) * scale + margin + self.offset_y
            return canvas_x, canvas_y
        
        self.canvas_objects = {}
        
        for member in dzialki_to_draw:
            coords = self.parse_coordinates(member.geometry)
            canvas_coords = []
            for x, y in coords:
                canvas_coords.extend(transform(x, y))
            
            polygon_id = self.canvas.create_polygon(canvas_coords, fill='', outline='#00008B', width=2, tags="clickable")
            self.canvas_objects[polygon_id] = member
            
            if hasattr(member, 'parcel_id') and member.parcel_id:
                center_x = sum(coords[i][0] for i in range(len(coords))) / len(coords)
                center_y = sum(coords[i][1] for i in range(len(coords))) / len(coords)
                label_x, label_y = transform(center_x, center_y)

                parts = member.parcel_id.split('.')
                label_text = parts[2] if len(parts) > 2 else member.parcel_id
                self.canvas.create_text(label_x, label_y, text=label_text, fill='#00008B', font=('Arial', 8))
        
        for member in budynki_to_draw:
            coords = self.parse_coordinates(member.geometry)
            canvas_coords = []
            for x, y in coords:
                canvas_coords.extend(transform(x, y))
            
            polygon_id = self.canvas.create_polygon(canvas_coords, fill='', outline='#FF0000', width=1, tags="clickable")
            self.canvas_objects[polygon_id] = member
            
            if hasattr(member, 'building_function') and member.building_function:
                center_x = sum(coords[i][0] for i in range(len(coords))) / len(coords)
                center_y = sum(coords[i][1] for i in range(len(coords))) / len(coords)
                label_x, label_y = transform(center_x, center_y)
                self.canvas.create_text(label_x, label_y, text=member.building_function, fill='#FF0000', font=('Arial', 8))

        for member in kontury_to_draw:
            coords = self.parse_coordinates(member.geometry)
            canvas_coords = []
            for x, y in coords:
                canvas_coords.extend(transform(x, y))
            
            self.canvas.create_polygon(canvas_coords, fill='', outline='#00FF00', width=1, dash=(4, 2))
            
            if hasattr(member, 'ozu') or hasattr(member, 'ozk'):
                center_x = sum(coords[i][0] for i in range(len(coords))) / len(coords)
                center_y = sum(coords[i][1] for i in range(len(coords))) / len(coords)
                label_x, label_y = transform(center_x, center_y)
                ozu = member.ozu if hasattr(member, 'ozu') and member.ozu else ''
                ozk = member.ozk if hasattr(member, 'ozk') and member.ozk else ''
                label = f"{ozu}{ozk}" if ozu or ozk else ''
                if label:
                    self.canvas.create_text(label_x, label_y, text=label, fill='#008000', font=('Arial', 8))
        
        for member in punkty_to_draw:
            coords_str = member.geometry.strip()
            numbers = coords_str.split()
            if len(numbers) >= 2:
                x, y = float(numbers[0]), float(numbers[1])
                canvas_x, canvas_y = transform(x, y)
                
                radius = 2
                point_id = self.canvas.create_oval(
                    canvas_x - radius, canvas_y - radius,
                    canvas_x + radius, canvas_y + radius,
                    fill='black', outline='black', width=1, tags="clickable"
                )
                self.canvas_objects[point_id] = member

        bbox = self.canvas.bbox("all")
        if bbox:
            extra_margin = 1000
            self.canvas.configure(scrollregion=(
                bbox[0] - extra_margin,
                bbox[1] - extra_margin,
                bbox[2] + extra_margin,
                bbox[3] + extra_margin
            ))
    
    def on_canvas_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        items = self.canvas.find_overlapping(x, y, x, y)

        for item in reversed(items):
            if item in self.canvas_objects:
                member = self.canvas_objects[item]
                self.show_object_info(member)
                break
    
    def show_object_info(self, member):
        """Wyświetla informacje o obiekcie"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        
        info = f"Typ obiektu:\n{member.feature_type}\n\n"
        info += f"Typ geometrii:\n{member.geometry_type}\n\n"
        
        if hasattr(member, 'point_id') and member.point_id:
            info += f"ID punktu:\n{member.point_id}\n\n"
        
        if hasattr(member, 'contour_id') and member.contour_id:
            info += f"ID konturu:\n{member.contour_id}\n\n"
            if hasattr(member, 'ozu') and member.ozu:
                info += f"OZU: {member.ozu}\n"
            if hasattr(member, 'ozk') and member.ozk:
                info += f"OZK: {member.ozk}\n"
            info += "\n"
        
        if hasattr(member, 'gml_id') and member.gml_id:
            info += f"ID obiektu:\n{member.gml_id}\n\n"

        if hasattr(member, 'parcel_id') and member.parcel_id:
            info += f"ID działki:\n{member.parcel_id}\n\n"
        
        # Dodatkowe informacje dla budynków
        if member.feature_type == 'egb:EGB_Budynek':
            if hasattr(member, 'building_id') and member.building_id:
                info += f"ID budynku:\n{member.building_id}\n\n"
            
            if hasattr(member, 'building_function') and member.building_function:
                function_map = {
                    'm': 'Mieszkalny',
                    'g': 'Gospodarczy',
                    'p': 'Przemysłowy',
                    'u': 'Użyteczności publicznej',
                    'i': 'Inne'
                }
                function_name = function_map.get(member.building_function, member.building_function)
                info += f"Typ budynku:\n{function_name}\n\n"
            
            if hasattr(member, 'floors_above') and member.floors_above is not None:
                info += f"Kondygnacje nadziemne: {member.floors_above}\n"
            
            if hasattr(member, 'floors_below') and member.floors_below is not None:
                info += f"Kondygnacje podziemne: {member.floors_below}\n"
            
            if hasattr(member, 'built_area') and member.built_area:
                info += f"Powierzchnia zabudowy: {member.built_area} m²\n"
            
            info += "\n"
        
        if hasattr(member, 'area') and member.area:
            info += f"Powierzchnia:\n{member.area} ha\n\n"
        
        # Dodatkowe informacje dla działek
        if member.feature_type == 'egb:EGB_DzialkaEwidencyjna':
            # Policz budynki wewnątrz działki
            if self.reader and hasattr(member, 'gml_id') and member.gml_id:
                building_count = 0
                for other in self.reader.members:
                    if other.feature_type == 'egb:EGB_Budynek':
                        for line in other.feature_data:
                            if 'dzialkaZabudowana' in line and member.gml_id in line:
                                building_count += 1
                                break
                
                info += f"Liczba budynków: {building_count}\n\n"
        
        if hasattr(member, 'classuse') and member.classuse:
            info += "Klasyfikacja użytkowania:\n"
            for i in member.classuse:
                ofu = i.get('OFU', '')
                ozu = i.get('OZU', '')
                ozk = i.get('OZK', '')
                pow = i.get('powierzchnia', 0)
                if ofu == ozu:
                    info += f" - {ofu}{ozk}: {pow} ha\n"
                elif ofu and ozu and ozk:
                    info += f" - {ofu}-{ozu}{ozk}: {pow} ha\n"
                else:
                    info += f" - {ofu}: {pow} ha\n"

        self.info_text.insert("1.0", info)
        self.info_text.config(state=tk.DISABLED)
    
    def on_mouse_wheel(self, event):
        """Obsługa zoomu kółkiem myszy"""
        if self.reader is None:
            return
        
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        
        old_zoom = self.zoom_level
        if event.delta > 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level /= 1.1
        
        self.zoom_level = max(0.1, min(self.zoom_level, 50.0))
        
        zoom_ratio = self.zoom_level / old_zoom
        self.offset_x = mouse_x + (self.offset_x - mouse_x) * zoom_ratio
        self.offset_y = mouse_y + (self.offset_y - mouse_y) * zoom_ratio
        
        self.update_display()
    
    def on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_drag_motion(self, event):
        if self.reader is None:
            return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.offset_x += dx
        self.offset_y += dy
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.update_display()
    
    def parse_coordinates(self, geometry_string):
        try:
            coords_str = geometry_string.strip()
            numbers = coords_str.split()
            
            coords = []
            for i in range(0, len(numbers), 2):
                if i + 1 < len(numbers):
                    x = float(numbers[i])
                    y = float(numbers[i + 1])
                    coords.append((x, y))
            
            return coords
        except Exception as e:
            return []

def main():
    root = tk.Tk()
    app = GmlViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
