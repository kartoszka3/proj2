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
        
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.import_btn = ttk.Button(control_frame, text="Wczytaj dane", command=self.import_gml)
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        self.browse_btn = ttk.Button(control_frame, text="📁", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, padx=5)

        self.var_dzialki = tk.BooleanVar(value=True)
        self.var_budynki = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(control_frame, text="Działki", variable=self.var_dzialki, 
                       command=self.update_display).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Budynki", variable=self.var_budynki,
                       command=self.update_display).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Gotowy do importu")
        self.status_label.pack(side=tk.LEFT, padx=20)

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
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Wybierz plik GML",
            filetypes=[("Pliki GML", "*.gml *.txt"), ("Wszystkie pliki", "*.*")],
            initialdir=r"C:\uni\5sem\kataster\proj2\dane"
        )
        if filename:
            self.current_path = filename
            self.status_label.config(text=f"Wybrano: {filename.split('/')[-1]}")
        
    def import_gml(self):
        try:
            self.status_label.config(text="Wczytywanie...")
            self.root.update()
            
            self.reader = GmlReader(self.current_path)
            
            count_dzialki = sum(1 for m in self.reader.members if m.feature_type == 'egb:EGB_DzialkaEwidencyjna')
            count_budynki = sum(1 for m in self.reader.members if m.feature_type == 'egb:EGB_Budynek')
            
            self.status_label.config(text=f"Wczytano: {count_dzialki} działek, {count_budynki} budynków")
            
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać pliku: {str(e)}")
            self.status_label.config(text="Błąd importu")
    
    def update_display(self):
        if self.reader is None:
            return
        
        self.canvas.delete("all")
        
        global show_dzialki, show_budynki
        show_dzialki = self.var_dzialki.get()
        show_budynki = self.var_budynki.get()
        
        all_coords = []
        objects_to_draw = []
        
        for member in self.reader.members:
            if member.geometry_type == 'Polygon' and member.geometry:
                if member.feature_type == 'egb:EGB_DzialkaEwidencyjna' and not show_dzialki:
                    continue
                if member.feature_type == 'egb:EGB_Budynek' and not show_budynki:
                    continue
                
                coords = self.parse_coordinates(member.geometry)
                if coords:
                    all_coords.extend(coords)
                    objects_to_draw.append(member)
        
        xs = [c[0] for c in all_coords]
        ys = [c[1] for c in all_coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 980
        canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 600
        
        margin = 50
        scale_x = (canvas_width - 2 * margin) / (max_x - min_x) if max_x != min_x else 1
        scale_y = (canvas_height - 2 * margin) / (max_y - min_y) if max_y != min_y else 1
        scale = min(scale_x, scale_y)
        
        def transform(x, y):
            canvas_x = (x - min_x) * scale + margin
            canvas_y = (y - min_y) * scale + margin
            return canvas_x, canvas_y
        
        # Wyczyść mapowanie obiektów
        self.canvas_objects = {}
        
        for member in objects_to_draw:
            coords = self.parse_coordinates(member.geometry)
            canvas_coords = []
            for x, y in coords:
                canvas_coords.extend(transform(x, y))
            
            if member.feature_type == 'egb:EGB_DzialkaEwidencyjna':
                color = '#90EE90'  # Jasny zielony
                outline = '#006400'  # Ciemny zielony
            else:  # Budynek
                color = '#FFB6C1'  # Jasny różowy
                outline = '#8B0000'  # Ciemny czerwony
            
            # Utwórz polygon i zapisz mapowanie
            polygon_id = self.canvas.create_polygon(canvas_coords, fill=color, outline=outline, width=1, tags="clickable")
            self.canvas_objects[polygon_id] = member
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_click(self, event):
        """Obsługuje kliknięcie na canvas"""
        # Pobierz obiekt pod kursorem
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        items = self.canvas.find_overlapping(x, y, x, y)
        
        for item in items:
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
        
        if hasattr(member, 'gml_id') and member.gml_id:
            info += f"ID obiektu:\n{member.gml_id}\n\n"
        
        if hasattr(member, 'area') and member.area:
            info += f"Powierzchnia:\n{member.area} ha\n\n"
        
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
