import unittest                # Python'ın test framework'ü
import numpy as np            # Sayısal işlemler için NumPy
import tkinter as tk          # GUI oluşturmak için
from matplotlib.figure import Figure  # Matplotlib grafik oluşturma
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Matplotlib'i Tkinter'da göstermek için
from parking_system import ParkingSystem  # Ana park sistemi sınıfı

class VisualTestWindow:
    """(KRITIK) Test sonuçlarını görsel olarak gösteren pencere sınıfı"""
    def __init__(self, title, grid, start_pos=None, target_pos=None, path=None):
        self.root = tk.Tk()
        self.root.title(title)
        
        # Pencere boyutu ayarla
        self.root.geometry("800x800")
        
        # Matplotlib figure oluştur
        self.fig = Figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111)
        
        # Tkinter canvas'ı oluştur
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
        
        # Grid'i görselleştir
        self.visualize_grid(grid, start_pos, target_pos, path)
        
        # Sonraki teste geçiş butonu
        self.close_button = tk.Button(self.root, text="Sonraki Test", command=self.root.destroy)
        self.close_button.pack(pady=10)
        
        # Pencere kapanana kadar bekle
        self.root.mainloop()
    
    def visualize_grid(self, grid, start_pos, target_pos, path):
        """(KRITIK) Test grid'ini ve sonuçlarını görselleştirir"""
        self.ax.clear()
        
        # Renk matrisini oluştur
        colors = np.zeros((*grid.shape, 3))
        colors[grid == 1] = [1, 0, 0]  # Kırmızı: dolu
        colors[grid == 0] = [0, 0.8, 0]  # Yeşil: boş
        
        # Grid'i göster
        self.ax.imshow(colors)
        
        # Grid çizgilerini ekle
        for i in range(grid.shape[0] + 1):
            self.ax.axhline(y=i-0.5, color='black', linestyle='-', alpha=0.2)
        for j in range(grid.shape[1] + 1):
            self.ax.axvline(x=j-0.5, color='black', linestyle='-', alpha=0.2)
        
        # Başlangıç noktasını göster
        if start_pos:
            self.ax.plot(start_pos[1], start_pos[0], 'ko', markersize=10, label='Başlangıç')
        
        # Hedef noktayı göster
        if target_pos:
            self.ax.plot(target_pos[1], target_pos[0], 'bo', markersize=10, label='Hedef')
        
        # Rotayı çiz
        if path:
            path_y = [pos[0] for pos in path]
            path_x = [pos[1] for pos in path]
            self.ax.plot(path_x, path_y, 'yellow', linewidth=2, label='Rota')
        
        self.ax.grid(False)
        self.ax.legend()
        self.fig.canvas.draw()

class TestParkingSystem(unittest.TestCase):
    """(KRITIK) Park sisteminin test sınıfı"""
    def setUp(self):
        """Her test öncesi çalışacak hazırlık fonksiyonu"""
        self.test_counter = 1  # Test sayacı
        self.parking = ParkingSystem(20, 20)  # Test için park sistemi örneği
    
    def visualize_test(self, title, grid, start_pos=None, target_pos=None, path=None):
        """Test sonuçlarını görselleştirme yardımcı fonksiyonu"""
        print(f"\nTest {self.test_counter}: {title}")
        VisualTestWindow(f"Test {self.test_counter}: {title}", grid, start_pos, target_pos, path)
        self.test_counter += 1

    def test_1_grid_initialization(self):
        """(KRITIK) Grid başlatma ve boyut kontrolü testi"""
        print("\nTest 1: Grid Başlatma Testi")
        self.assertEqual(self.parking.grid.shape, (20, 20))  # Grid boyutunu kontrol et
        
        # Doluluk oranını kontrol et (%60 ±%10)
        occupied_count = np.count_nonzero(self.parking.grid == 1)
        total_spots = 20 * 20
        occupancy_rate = occupied_count / total_spots
        self.assertAlmostEqual(occupancy_rate, 0.6, delta=0.1)
        
        self.visualize_test("Grid Başlatma Testi", self.parking.grid)

    def test_2_check_surroundings(self):
        """(KRITIK) Noktanın çevresinin kontrolü testi"""
        print("\nTest 2: Çevre Kontrol Testi")
        
        # 4 tarafı boş olan nokta test senaryosu
        test_grid = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ])
        self.parking.grid = test_grid
        self.parking.rows = 3
        self.parking.columns = 3
        self.assertTrue(self.parking.check_surroundings(1, 1))
        
        self.visualize_test("Çevre Kontrol Testi - Tüm Çevresi Boş", test_grid, (1, 1))

    def test_3_nearest_empty_spot_basic(self):
        """(KRITIK) Basit en yakın boş nokta bulma testi"""
        print("\nTest 3: En Yakın Boş Yer Testi (Temel)")
        
        # Basit 2x2 grid test senaryosu
        test_grid = np.array([
            [1, 0],
            [1, 1]
        ])
        self.parking.grid = test_grid
        self.parking.rows = 2
        self.parking.columns = 2
        nearest = self.parking.find_nearest_empty_spot((0, 0))
        self.assertEqual(nearest, (0, 1))  # En yakın boş yerin doğruluğunu kontrol et
        
        path = self.parking.calculate_path((0, 0), nearest)
        self.visualize_test("En Yakın Boş Yer Testi", test_grid, (0, 0), nearest, path)

    def test_4_nearest_empty_spot_surrounded(self):
        """(KRITIK) 4 tarafı boş nokta özel durum testi"""
        print("\nTest 4: 4 Tarafı Boş Olan Nokta Testi")
        
        # 4 tarafı boş olan nokta test senaryosu
        test_grid = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ])
        self.parking.grid = test_grid
        self.parking.rows = 3
        self.parking.columns = 3
        nearest = self.parking.find_nearest_empty_spot((1, 1))
        
        path = self.parking.calculate_path((1, 1), nearest)
        self.visualize_test("4 Tarafı Boş Olan Nokta Testi", test_grid, (1, 1), nearest, path)

    def test_5_complex_scenario(self):
        """(KRITIK) Karmaşık senaryo kapsamlı testi"""
        print("\nTest 5: Karmaşık Senaryo Testi")
        
        # Karmaşık test grid'i
        test_grid = np.array([
            [1, 1, 1, 0],
            [1, 1, 0, 1],
            [1, 0, 1, 1],
            [0, 1, 1, 1]
        ])
        self.parking.grid = test_grid
        self.parking.rows = 4
        self.parking.columns = 4
        start_pos = (0, 0)
        nearest = self.parking.find_nearest_empty_spot(start_pos)
        
        # (KRITIK) Manhattan mesafelerini hesapla ve yazdır
        print("\nDolu kutucukların başlangıç noktasına olan Manhattan mesafeleri:")
        print("Format: (x, y) = mesafe")
        print("-" * 40)
        
        # Dolu noktaların mesafelerini hesapla
        occupied_spots = []
        for i in range(self.parking.rows):
            for j in range(self.parking.columns):
                if test_grid[i][j] == 1:
                    distance = self.parking.calculate_manhattan_distance(start_pos, (i, j))
                    occupied_spots.append(((i, j), distance))
        
        # Mesafelere göre sırala
        occupied_spots.sort(key=lambda x: x[1])
        
        # Dolu noktaların mesafelerini yazdır
        for spot, distance in occupied_spots:
            if spot == start_pos:
                print(f"({spot[0]}, {spot[1]}) = {distance} (Başlangıç Noktası)")
            else:
                print(f"({spot[0]}, {spot[1]}) = {distance}")
        
        # Boş noktaların mesafelerini hesapla ve yazdır
        print("\nBoş park yerleri:")
        empty_spots = []
        for i in range(self.parking.rows):
            for j in range(self.parking.columns):
                if test_grid[i][j] == 0:
                    distance = self.parking.calculate_manhattan_distance(start_pos, (i, j))
                    empty_spots.append(((i, j), distance))
        
        empty_spots.sort(key=lambda x: x[1])
        for spot, distance in empty_spots:
            if spot == nearest:
                print(f"({spot[0]}, {spot[1]}) = {distance} (En Yakın Boş Yer)")
            else:
                print(f"({spot[0]}, {spot[1]}) = {distance}")
        
        # Rotayı hesapla ve yazdır
        path = self.parking.calculate_path(start_pos, nearest)
        print(f"\nSeçilen rota: {' -> '.join([str(pos) for pos in path])}")
        
        self.visualize_test("Karmaşık Senaryo Testi", test_grid, start_pos, nearest, path)

def main():
    """Ana test programı"""
    # Test suitini oluştur ve çalıştır
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParkingSystem)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()