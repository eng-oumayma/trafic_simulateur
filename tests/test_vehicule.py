
import pytest

from models.vehicule import Vehicule
from models.route import Route

class TestVehicule:
    def setup_method(self):
        """Initialise un véhicule avant chaque test."""
        self.vehicule = Vehicule("V1", ["R1", "R2"])


    def test_initialisation(self, vehicule_valide):
        assert vehicule_valide.identifiant == "V1"
        assert vehicule_valide.itineraire == ["R1", "R2"]
        assert vehicule_valide.index_route == 0
        assert vehicule_valide.route_actuelle is None
        assert vehicule_valide.position == 0.0
        assert vehicule_valide.vitesse == 0.0
        assert vehicule_valide.temps_creation == 0.0
        assert vehicule_valide.temps_arrivee is None
        assert vehicule_valide.distance_parcourue == 0.0
        assert vehicule_valide.temps_arret == 0.0
        assert vehicule_valide.arrive is False

    def test_initialisation_avec_temps_creation(self):
        v = Vehicule("V2", ["R1"], temps_creation=5.0)

        assert v.temps_creation == 5.0

    def test_copie_itineraire(self):
        itineraire = ["R1", "R2"]
        v = Vehicule("V3", itineraire)
        itineraire.append("R3")

        assert v.itineraire == ["R1", "R2"]

    def test_avancer_deplacement_normal(self):
        self.vehicule.avancer(2.0, 10.0, 100.0)

        assert self.vehicule.position == pytest.approx(20.0)
        assert self.vehicule.vitesse == pytest.approx(10.0)
        assert self.vehicule.distance_parcourue == pytest.approx(20.0)

    def test_avancer_limite_par_fin_route(self):
        self.vehicule.position = 90.0

        self.vehicule.avancer(5.0, 10.0, 100.0)

        assert self.vehicule.position == pytest.approx(100.0)
        assert self.vehicule.vitesse == pytest.approx(2.0)
        assert self.vehicule.distance_parcourue == pytest.approx(10.0)

    def test_avancer_ne_recule_pas(self):
        self.vehicule.position = 10.0

        self.vehicule.avancer(2.0, -5.0, 100.0)

        assert self.vehicule.position == pytest.approx(10.0)
        assert self.vehicule.vitesse == pytest.approx(0.0)
        assert self.vehicule.distance_parcourue == pytest.approx(0.0)

    def test_avancer_limite_par_obstacle(self):
        self.vehicule.position = 10.0

        self.vehicule.avancer(5.0, 10.0, 25.0)

        assert self.vehicule.position == pytest.approx(25.0)
        assert self.vehicule.vitesse == pytest.approx(3.0)

    def test_temps_arret_si_vitesse_inferieure_a_05(self):
        self.vehicule.avancer(2.0, 0.4, 100.0)

        assert self.vehicule.temps_arret == pytest.approx(2.0)

    def test_pas_de_temps_arret_si_vitesse_egale_a_05(self):
        self.vehicule.avancer(2.0, 0.5, 100.0)

        assert self.vehicule.temps_arret == pytest.approx(0.0)

    def test_accumulation_temps_arret(self):
        self.vehicule.avancer(2.0, 0.0, 100.0)
        self.vehicule.avancer(3.0, 0.2, 100.0)

        assert self.vehicule.temps_arret == pytest.approx(5.0)

    def test_route_suivante(self):
        assert self.vehicule.route_suivante() == "R2"

    def test_route_suivante_sur_derniere_route(self):
        v = Vehicule("V4", ["R1"])
        assert v.route_suivante() is None

    def test_changer_de_route(self):
        r1 = Route("R1", 100, 50, "A", "B")
        r2 = Route("R2", 100, 50, "B", "C")

        r1.ajouter_vehicule(self.vehicule)
        resultat = self.vehicule.changer_de_route(r2)

        assert resultat is True
        assert self.vehicule not in r1.vehicules
        assert self.vehicule in r2.vehicules
        assert self.vehicule.route_actuelle is r2
        assert self.vehicule.position == pytest.approx(0.0)
        assert self.vehicule.index_route == 1

    def test_changement_refuse_si_route_saturee(self):
        r1 = Route("R1", 100, 50, "A", "B")
        r2 = Route("R2", 7, 50, "B", "C")

        r1.ajouter_vehicule(self.vehicule)

        # Remplit la capacité de R2.
        bloqueur = Vehicule("V2", ["R2"])
        assert r2.ajouter_vehicule(bloqueur)

        resultat = self.vehicule.changer_de_route(r2)

        assert resultat is False
        assert self.vehicule in r1.vehicules
        assert self.vehicule.route_actuelle is r1
        assert self.vehicule.index_route == 0

    def test_temps_parcours_avant_arrivee(self):
        assert self.vehicule.temps_parcours() is None

    def test_temps_parcours_apres_arrivee(self):
        self.vehicule.temps_creation = 5.0
        self.vehicule.temps_arrivee = 25.0

        assert self.vehicule.temps_parcours() == pytest.approx(20.0)

    def test_repr_sans_route(self):
        assert repr(self.vehicule) == "Vehicule(V1, route=None, pos=0m)"

    def test_repr_avec_route(self):
        route = Route("R1", 100, 50, "A", "B")
        route.ajouter_vehicule(self.vehicule)
        self.vehicule.position = 12.0

        assert repr(self.vehicule) == "Vehicule(V1, route=R1, pos=12m)"
