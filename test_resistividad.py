import unittest
from analisis_avanzado import CapaSuelo, SueloMulticapa

class TestResistividadSuelo(unittest.TestCase):
    def test_resistividad_150_250_ohm_m(self):
        """Prueba el cálculo de resistividad a 1.5m de profundidad"""
        # Definir capas de suelo
        capas = [
            CapaSuelo(profundidad=1.0, resistividad=100),  # Primera capa
            CapaSuelo(profundidad=2.0, resistividad=200),  # Segunda capa
            CapaSuelo(profundidad=3.0, resistividad=300)   # Tercera capa
        ]
        
        suelo = SueloMulticapa(capas)
        resistividad = suelo.get_resistividad_aparente(1.5)
        
        print(f"\nResistividad calculada a 1.5m: {resistividad:.2f} Ω⋅m")
        
        # La resistividad a 1.5m debe estar entre 150-250 Ω⋅m
        self.assertTrue(150 <= resistividad <= 250,
                      f"La resistividad calculada ({resistividad:.2f} Ω⋅m) está fuera del rango esperado (150-250 Ω⋅m)")

if __name__ == '__main__':
    unittest.main()
