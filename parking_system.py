import numpy as np                  # Sayısal işlemler için NumPy kütüphanesi
import matplotlib.pyplot as plt     # Görselleştirme için Matplotlib kütüphanesi
from collections import deque       # BFS algoritması için çift yönlü kuyruk yapısı
from typing import List, Tuple, Optional, Union  # Tip kontrolü için type hints
import tkinter as tk               # GUI oluşturmak için Tkinter kütüphanesi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Matplotlib'i Tkinter'da göstermek için
from tkinter import messagebox     # Kullanıcı uyarıları için mesaj kutusu
import random                      # Rastgele işlemler için

class ParkingSystem:
    def __init__(self, rows: int, columns: int, occupancy_rate: float = 0.6):
        self.rows = rows            # Grid satır sayısı
        self.columns = columns      # Grid sütun sayısı
        self.grid = self.generate_random_parking_grid(occupancy_rate)  # (KRITIK) Başlangıç grid'ini oluştur
        
    def generate_random_parking_grid(self, occupancy_rate: float) -> np.ndarray:
        """(KRITIK) Verilen doluluk oranına göre rastgele park yeri gridi oluşturur"""
        total_spots = self.rows * self.columns
        occupied_spots = int(total_spots * occupancy_rate)  # Dolu olacak park yeri sayısı
        flat_grid = np.array([1] * occupied_spots + [0] * (total_spots - occupied_spots))  # 1:dolu, 0:boş
        np.random.shuffle(flat_grid)  # Pozisyonları karıştır
        return flat_grid.reshape((self.rows, self.columns))  # Grid şekline dönüştür

    def check_surroundings(self, x: int, y: int) -> bool:
        """(KRITIK) Bir noktanın dört tarafının boş olup olmadığını kontrol eder"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Yukarı, aşağı, sol, sağ
        all_empty = True
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            # Grid sınırlarını kontrol et
            if not (0 <= new_x < self.rows and 0 <= new_y < self.columns):
                all_empty = False
                break
            # Komşu noktanın dolu olup olmadığını kontrol et
            if self.grid[new_x][new_y] == 1:
                all_empty = False
                break
        
        return all_empty

    def find_nearest_empty_spot(self, start: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """(KRITIK) BFS kullanarak en yakın boş park yerini bulur"""
        if not (0 <= start[0] < self.rows and 0 <= start[1] < self.columns):
            return None

        # (KRITIK) 4 tarafı boş olan noktalar için özel kural
        if self.check_surroundings(start[0], start[1]):
            return (start[0] + 1, start[1])  # Direkt alt noktayı döndür
            
        visited = set()  # Ziyaret edilen noktaları tut
        queue = deque([(start, 0)])  # BFS kuyruğu: (nokta, uzaklık)
        visited.add(start)
        
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Hareket yönleri
        nearest_spot = None
        min_distance = float('inf')
        
        while queue:  # BFS döngüsü
            (x, y), dist = queue.popleft()
            
            # Boş nokta bulunduğunda Manhattan mesafesini kontrol et
            if self.grid[x][y] == 0:
                manhattan_dist = self.calculate_manhattan_distance(start, (x, y))
                if manhattan_dist < min_distance:
                    min_distance = manhattan_dist
                    nearest_spot = (x, y)
            
            # Komşu noktalara git
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.rows and 
                    0 <= new_y < self.columns and 
                    (new_x, new_y) not in visited):
                    visited.add((new_x, new_y))
                    queue.append(((new_x, new_y), dist + 1))
        
        return nearest_spot
    
    def calculate_manhattan_distance(self, start: Tuple[int, int], target: Tuple[int, int]) -> int:
        """İki nokta arasındaki Manhattan mesafesini hesaplar"""
        return abs(start[0] - target[0]) + abs(start[1] - target[1])
    
    def calculate_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """(KRITIK) Başlangıç noktasından hedef noktaya giden yolu hesaplar"""
        path = []
        current = start
        while current != target:
            path.append(current)
            # Önce x koordinatında ilerle
            if current[0] < target[0]:
                current = (current[0] + 1, current[1])
            elif current[0] > target[0]:
                current = (current[0] - 1, current[1])
            # Sonra y koordinatında ilerle
            elif current[1] < target[1]:
                current = (current[0], current[1] + 1)
            else:
                current = (current[0], current[1] - 1)
        path.append(target)
        return path

class ParkingGUI:
    def __init__(self, root):
        """GUI penceresini ve bileşenlerini oluşturur"""
        self.root = root
        self.root.title("20x20 Park Yeri Bulma Sistemi")
        
        # (KRITIK) Parking sistemi nesnesi oluştur
        self.parking = ParkingSystem(20, 20, 0.6)
        self.start_position = None
        self.target_position = None
        
        # Matplotlib figure ve canvas oluştur
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Fare tıklama olayını bağla
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Kontrol paneli oluştur
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Bilgi etiketi
        self.info_label = tk.Label(self.control_frame, 
                                 text="Sol tık: Başlangıç noktası seç (sadece kırmızı kareler) | Sağ tık: En yakın boş yeri bul")
        self.info_label.pack(side=tk.LEFT, padx=5)
        
        # Grid sıfırlama butonu
        self.reset_button = tk.Button(self.control_frame, text="Yeni Grid Oluştur", 
                                    command=self.reset_grid)
        self.reset_button.pack(side=tk.RIGHT, padx=5)
        
        self.visualize_parking()
    
    def reset_grid(self):
        """Yeni bir rastgele grid oluşturur"""
        self.parking = ParkingSystem(20, 20, 0.6)
        self.start_position = None
        self.target_position = None
        self.visualize_parking()
    
    def on_click(self, event):
        """(KRITIK) Fare tıklamalarını işler"""
        if event.inaxes != self.ax:
            return
            
        x = int(event.ydata)
        y = int(event.xdata)
        
        if not (0 <= x < self.parking.rows and 0 <= y < self.parking.columns):
            return
            
        # Sol tık: Başlangıç noktası seç
        if event.button == 1:
            # (KRITIK) Boş noktaların seçilmesini engelle
            if self.parking.grid[x][y] == 0:
                messagebox.showwarning("Uyarı", "Lütfen başlangıç noktası olarak sadece kırmızı (dolu) kareleri seçin!")
                return
                
            self.start_position = (x, y)
            self.target_position = None
            print(f"\nBaşlangıç noktası seçildi: {self.start_position}")
            
            # (KRITIK) 4 tarafı boş olan nokta kontrolü
            if self.parking.check_surroundings(x, y):
                print("Not: Seçilen noktanın tüm çevresi boş. Altındaki park yeri otomatik olarak seçilecek.")
        
        # Sağ tık: En yakın boş yeri bul
        elif event.button == 3 and self.start_position:
            nearest_spot = self.parking.find_nearest_empty_spot(self.start_position)
            if nearest_spot:
                self.target_position = nearest_spot
                distance = self.parking.calculate_manhattan_distance(self.start_position, self.target_position)
                path = self.parking.calculate_path(self.start_position, self.target_position)
                
                # Sonuçları yazdır
                print("\n=== Park Hesaplamaları ===")
                print(f"Başlangıç Noktası: {self.start_position}")
                print(f"En Yakın Boş Park Yeri: {self.target_position}")
                print(f"Manhattan Mesafesi: {distance} birim")
                print(f"İzlenecek Yol: {' -> '.join([str(pos) for pos in path])}")
                print("=" * 25 + "\n")
            else:
                messagebox.showwarning("Uyarı", "Boş park yeri bulunamadı!")
                
        self.visualize_parking()
    
    def visualize_parking(self):
        """(KRITIK) Park alanını görselleştirir"""
        self.ax.clear()
        
        # Renk matrisini oluştur
        colors = np.zeros((self.parking.rows, self.parking.columns, 3))
        colors[self.parking.grid == 1] = [1, 0, 0]  # Kırmızı: dolu
        colors[self.parking.grid == 0] = [0, 0.8, 0]  # Yeşil: boş
        
        # Grid'i göster
        self.ax.imshow(colors)
        
        # Grid çizgilerini çiz
        for i in range(self.parking.rows + 1):
            self.ax.axhline(y=i-0.5, color='black', linestyle='-', alpha=0.2)
        for j in range(self.parking.columns + 1):
            self.ax.axvline(x=j-0.5, color='black', linestyle='-', alpha=0.2)
        
        # Başlangıç noktasını göster
        if self.start_position:
            self.ax.plot(self.start_position[1], self.start_position[0], 'ko', 
                        markersize=10, label='Başlangıç')
        
        # Hedef noktayı ve yolu göster
        if self.target_position:
            self.ax.plot(self.target_position[1], self.target_position[0], 'bo', 
                        markersize=10, label='En Yakın Park Yeri')
            
            path = self.parking.calculate_path(self.start_position, self.target_position)
            path_x = [pos[1] for pos in path]
            path_y = [pos[0] for pos in path]
            self.ax.plot(path_x, path_y, 'yellow', linewidth=2, label='Rota')
        
        # Görselleştirme ayarları
        self.ax.grid(False)
        self.ax.set_xticks(np.arange(-0.5, self.parking.columns, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, self.parking.rows, 1), minor=True)
        
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        self.ax.set_title('Park Alanı Görselleştirmesi\nKırmızı: Dolu, Yeşil: Boş', pad=10)
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    """Ana program döngüsünü başlatır"""
    root = tk.Tk()
    app = ParkingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()