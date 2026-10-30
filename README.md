# Simulateur de trafic routier

Simulateur modulaire de trafic : réseau (routes, intersections à feux),
véhicules, statistiques (vitesses, congestion, temps de parcours) et
rapports (console, CSV/JSON, graphiques).

## Installation

```bash
pip install -e .            # utilisation
pip install -e ".[dev,docs]"  # + tests et documentation
```

## Utilisation

```bash
simulateur-trafic --config data/config_reseau.json --tours 60 --delta-t 60
simulateur-trafic --version
```

ou en Python :

```python
from core.simulateur import Simulateur
Simulateur(fichier_config="data/config_reseau.json").lancer_simulation(60, 60)
```

## Tests et documentation

```bash
pytest                              # ou : python -m unittest discover -s tests
cd docs && python -m sphinx -b html . _build/html
```

## Licence

MIT — voir [LICENSE](LICENSE).
