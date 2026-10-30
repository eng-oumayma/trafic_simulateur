"""Tests unitaires du simulateur (exécutables avec pytest ou unittest).

Couvre les véhicules, les routes (collisions, saturation), le réseau
(feux, itinéraires), la simulation complète (conservation des véhicules,
reproductibilité, exports) et la détection de congestion.
"""
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.vehicule import Vehicule
from models.route import Route
from models.reseau import ReseauRoutier, Intersection
from core.simulateur import Simulateur
from core.analyseur import Analyseur

CONFIG = {
    "intersections": [
        {"id": "A", "x": 0, "y": 0},
        {"id": "B", "x": 1, "y": 0,
         "feux": [{"routes": ["A-B"], "duree": 30}, {"routes": ["C-B"], "duree": 30}]},
        {"id": "C", "x": 2, "y": 0},
    ],
    "routes": [
        {"nom": "A-B", "origine": "A", "destination": "B", "longueur": 800, "limite_vitesse": 50},
        {"nom": "B-C", "origine": "B", "destination": "C", "longueur": 800, "limite_vitesse": 50},
        {"nom": "C-B", "origine": "C", "destination": "B", "longueur": 800, "limite_vitesse": 50},
        {"nom": "B-A", "origine": "B", "destination": "A", "longueur": 800, "limite_vitesse": 50},
    ],
    "generation": {"seed": 1, "vehicules_initiaux": 5, "taux_apparition": 10,
                   "points_entree": ["A-B", "C-B"]},
}


class TestVehicule(unittest.TestCase):
    """Tests de :class:`models.vehicule.Vehicule`."""
    def test_avancer_respecte_la_limite(self):
        v = Vehicule("V1", ["R"])
        v.avancer(10, 20, limite_position=50)
        self.assertEqual(v.position, 50)
        self.assertAlmostEqual(v.vitesse, 5)

    def test_changer_de_route(self):
        r1, r2 = Route("R1", 500, 50, "A", "B"), Route("R2", 500, 50, "B", "C")
        v = Vehicule("V1", ["R1", "R2"])
        r1.ajouter_vehicule(v)
        self.assertTrue(v.changer_de_route(r2))
        self.assertEqual((v.route_actuelle, v.position, v.index_route), (r2, 0.0, 1))
        self.assertNotIn(v, r1.vehicules)


class TestRoute(unittest.TestCase):
    """Tests de :class:`models.route.Route`."""
    def test_pas_de_collision(self):
        r = Route("R", 1000, 50, "A", "B")
        for t in range(40):
            if t % 3 == 0:
                r.ajouter_vehicule(Vehicule(f"V{t}", ["R"]))
            r.mettre_a_jour_vehicules(5)
            pos = sorted(v.position for v in r.vehicules)
            for a, b in zip(pos, pos[1:]):
                self.assertGreaterEqual(b - a, Route.ECART_MIN - 1e-6)

    def test_saturation(self):
        r = Route("R", 70, 50, "A", "B")           # capacité = 10
        self.assertEqual(r.capacite, 10)
        self.assertTrue(r.ajouter_vehicule(Vehicule("V1", ["R"])))
        self.assertFalse(r.ajouter_vehicule(Vehicule("V2", ["R"])))  # même position

    def test_vitesse_diminue_avec_l_occupation(self):
        r = Route("R", 700, 50, "A", "B")
        v_vide = r.vitesse_desiree()
        for i in range(50):
            v = Vehicule(f"V{i}", ["R"]); v.position = i * 7.0
            r.vehicules.append(v); v.route_actuelle = r
        self.assertLess(r.vitesse_desiree(), v_vide)


class TestReseau(unittest.TestCase):
    """Tests de :class:`models.reseau.ReseauRoutier` et des feux."""
    def test_feux(self):
        i = Intersection("B", phases=[{"routes": ["X"], "duree": 30}, {"routes": ["Y"], "duree": 30}])
        self.assertTrue(i.est_vert("X", 10) and not i.est_vert("Y", 10))
        self.assertTrue(i.est_vert("Y", 40) and not i.est_vert("X", 40))
        self.assertTrue(i.est_vert("X", 60))            # cycle suivant
        self.assertTrue(i.est_vert("Z", 10))            # route hors feux

    def test_itineraire_valide_et_sans_demi_tour(self):
        res = ReseauRoutier.from_dict(CONFIG)
        chemin = res.itineraire_aleatoire(random.Random(0), "A-B")
        self.assertEqual(chemin[0], "A-B")
        for a, b in zip(chemin, chemin[1:]):
            self.assertIn(b, res.routes_suivantes(a))

    def test_route_dupliquee(self):
        res = ReseauRoutier.from_dict(CONFIG)
        with self.assertRaises(ValueError):
            res.ajouter_route(Route("A-B", 100, 50, "A", "B"))


class TestSimulation(unittest.TestCase):
    """Tests d'intégration de :class:`core.simulateur.Simulateur`."""
    def _lancer(self, seed=1):
        cfg = {**CONFIG, "generation": {**CONFIG["generation"], "seed": seed}}
        simu = Simulateur(config=cfg, afficher=False)
        return simu, simu.lancer_simulation(30, 60, exporter=False, graphiques=False)

    def test_conservation_des_vehicules(self):
        simu, r = self._lancer()
        self.assertEqual(r["vehicules_crees"], r["vehicules_arrives"] + r["vehicules_en_circulation"])
        self.assertGreater(r["vehicules_arrives"], 0)

    def test_reproductible(self):
        _, r1 = self._lancer(7)
        _, r2 = self._lancer(7)
        self.assertEqual(r1, r2)

    def test_vitesses_bornees(self):
        simu, _ = self._lancer()
        for e in simu.analyseur.historique_routes:
            self.assertLessEqual(e["vitesse_moyenne_kmh"], 50 + 1e-6)

    def test_temps_parcours_positifs(self):
        simu, _ = self._lancer()
        for v in simu.reseau.termines:
            self.assertGreater(v.temps_parcours(), 0)

    def test_export(self):
        with tempfile.TemporaryDirectory() as d:
            simu = Simulateur(config=CONFIG, afficher=False, dossier_sortie=d)
            simu.lancer_simulation(5, 60, exporter=True, graphiques=True)
            for f in ("historique.csv", "routes.csv", "trajets.csv", "resume.json",
                      "evolution.png", "congestion.png", "temps_parcours.png", "carte.png"):
                self.assertTrue(os.path.exists(os.path.join(d, f)), f)


class TestAnalyseur(unittest.TestCase):
    """Tests de :class:`core.analyseur.Analyseur`."""
    def test_detection_congestion(self):
        res = ReseauRoutier.from_dict(CONFIG)
        an = Analyseur()
        r = res.routes["A-B"]
        for i in range(3):                       # 3 véhicules quasi à l'arrêt
            v = Vehicule(f"V{i}", ["A-B"]); v.vitesse = 0.5; v.position = i * 7.0
            r.vehicules.append(v); v.route_actuelle = r
        for t in range(10):
            an.enregistrer(t * 60, res)
        zones = an.zones_congestion()
        self.assertEqual([z["route"] for z in zones], ["A-B"])
        self.assertAlmostEqual(zones[0]["frequence"], 1.0)


if __name__ == "__main__":
    unittest.main()
