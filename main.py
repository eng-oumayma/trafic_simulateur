"""Point d'entrée : lance une simulation de 60 minutes (pas de 1 minute) sur le
réseau décrit dans ``data/config_reseau.json``.
"""

from core.simulateur import Simulateur

if __name__ == "__main__":
    simu = Simulateur(fichier_config="data/config_reseau.json")
    simu.lancer_simulation(n_tours=60, delta_t=60)  # 60 minutes, pas de 1 min
