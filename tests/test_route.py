
import pytest

from models.route import Route
from models.vehicule import Vehicule

class TestRoute:

    def setup_method(self):
        """Prépare une route pour chaque test."""
        self.route = Route("R1", 100, 50, "A", "B")
        
    def test_initialisation(self, route_valide):
        """Vérifie la création d'une route avec la fixture."""
        assert route_valide.nom == "R1"
        assert route_valide.longueur == pytest.approx(100.0)
        assert route_valide.limite_vitesse == pytest.approx(50.0)
        assert route_valide.origine == "A"
        assert route_valide.destination == "B"
        assert route_valide.vehicules == []

    @pytest.mark.parametrize(
        "longueur, limite_vitesse",
        [
            (0, 50),
            (-10, 50),
            (100, 0),
            (100, -20),
            (0, 0),
        ],
    )
    def test_initialisation_valeurs_invalides(
        self, longueur, limite_vitesse
    ):
        with pytest.raises(ValueError):
            Route("R1", longueur, limite_vitesse, "A", "B")



@pytest.mark.parametrize(
    "longueur, vitesse, resultat_attendu",
    [
        # Deux cas normaux
        (100, 50, True),
        (500, 90, True),

        # Un cas limite : valeurs positives minimales
        (0.1, 0.1, True),

        # Deux cas invalides
        (0, 50, False),
        (100, -20, False),
    ]
)

def test_creation_route_parametree(
    longueur, vitesse, resultat_attendu
):
    """Teste la création d'une route avec plusieurs paramètres."""

    if resultat_attendu:
        route = Route(
            "R1", longueur, vitesse, "A", "B"
        )

        assert route.longueur == pytest.approx(longueur)
        assert route.limite_vitesse == pytest.approx(vitesse)
        assert route.nom == "R1"

    else:
        with pytest.raises(ValueError):
            Route("R1", longueur, vitesse, "A", "B")


    def test_capacite_route(self):
        assert self.route.capacite == 14

    def test_capacite_route_courte(self):
        route = Route("R2", 5, 30, "A", "B")
        assert route.capacite == 1

    def test_capacite_exactement_multiple_ecart(self):
        route = Route("R3", 21, 50, "A", "B")
        assert route.capacite == 3

    def test_taux_occupation_route_vide(self):
        assert self.route.taux_occupation == pytest.approx(0.0)

    def test_taux_occupation_apres_ajout(self):
        v = Vehicule("V1", ["R1"])
        self.route.ajouter_vehicule(v)

        assert self.route.taux_occupation == pytest.approx(
            1 / self.route.capacite
        )

    def test_vitesse_moyenne_route_vide(self):
        assert self.route.vitesse_moyenne_kmh() is None

    
    def test_vitesse_moyenne(self):
        v1 = Vehicule("V1", ["R1"])
        v2 = Vehicule("V2", ["R1"])

        assert self.route.ajouter_vehicule(v1) is True

        # Le premier véhicule doit s'éloigner de l'entrée.
        v1.position = Route.ECART_MIN

        assert self.route.ajouter_vehicule(v2) is True

        v1.vitesse = 10.0
        v2.vitesse = 20.0

        assert self.route.vitesse_moyenne_kmh() == pytest.approx(54.0)


    def test_a_de_la_place_route_vide(self):
        assert self.route.a_de_la_place() is True

    def test_ajouter_vehicule(self, route_valide, vehicule_valide):
        resultat = route_valide.ajouter_vehicule(vehicule_valide)

        assert resultat is True
        assert vehicule_valide in route_valide.vehicules
        assert vehicule_valide.route_actuelle is route_valide
        assert vehicule_valide.position == pytest.approx(0.0)

    def test_entree_refusee_si_vehicule_trop_proche(self):
        route = Route("R2", 100, 50, "A", "B")
        v1 = Vehicule("V1", ["R2"])
        v2 = Vehicule("V2", ["R2"])

        assert route.ajouter_vehicule(v1) is True
        assert route.ajouter_vehicule(v2) is False

        assert v2 not in route.vehicules
        assert v2.route_actuelle is None

    def test_entree_autorisee_si_ecart_suffisant(self):
        v1 = Vehicule("V1", ["R1"])
        v2 = Vehicule("V2", ["R1"])

        self.route.ajouter_vehicule(v1)
        v1.position = Route.ECART_MIN

        assert self.route.a_de_la_place() is True
        assert self.route.ajouter_vehicule(v2) is True

    def test_retirer_vehicule(self):
        v = Vehicule("V1", ["R1"])
        self.route.ajouter_vehicule(v)

        self.route.retirer_vehicule(v)

        assert v not in self.route.vehicules
        assert v.route_actuelle is None

    def test_retirer_vehicule_absent(self):
        v = Vehicule("V1", ["R1"])

        with pytest.raises(ValueError):
            self.route.retirer_vehicule(v)

    def test_vitesse_desiree_route_vide(self):
        vitesse_attendue = 50 / 3.6

        assert self.route.vitesse_desiree() == pytest.approx(
            vitesse_attendue
        )

    def test_vitesse_desiree_diminue_avec_occupation(self):
        v = Vehicule("V1", ["R1"])
        self.route.ajouter_vehicule(v)

        vitesse_vide = 50 / 3.6
        vitesse_occupee = self.route.vitesse_desiree()

        assert vitesse_occupee < vitesse_vide

    def test_vitesse_desiree_route_pleine(self):
        route = Route("R2", 7, 36, "A", "B")

        v = Vehicule("V1", ["R2"])
        route.ajouter_vehicule(v)

        assert route.taux_occupation == pytest.approx(1.0)
        assert route.vitesse_desiree() == pytest.approx(0.5)

    def test_mettre_a_jour_vehicules(self):
        v = Vehicule("V1", ["R1"])
        self.route.ajouter_vehicule(v)

        self.route.mettre_a_jour_vehicules(1.0)

        assert v.position > 0.0
        assert v.distance_parcourue > 0.0

    def test_pas_de_collision_entre_vehicules(self):
        route = Route("R2", 100, 50, "A", "B")

        v1 = Vehicule("V1", ["R2"])
        v2 = Vehicule("V2", ["R2"])

        route.ajouter_vehicule(v1)
        v1.position = 20.0
        route.ajouter_vehicule(v2)

        # Le véhicule le plus avancé est traité en premier.
        route.mettre_a_jour_vehicules(2.0)

        assert v1.position - v2.position >= (
            Route.ECART_MIN - 1e-9
        )

    def test_tete_de_file_route_vide(self):
        assert self.route.tete_de_file() is None

    def test_tete_de_file_avant_fin_route(self):
        v = Vehicule("V1", ["R1"])
        self.route.ajouter_vehicule(v)
        v.position = 50.0

        assert self.route.tete_de_file() is None

    def test_tete_de_file_fin_route(self):
        v = Vehicule("V1", ["R1"])
        self.route.ajouter_vehicule(v)
        v.position = self.route.longueur

        assert self.route.tete_de_file() is v

    def test_tete_de_file_choisit_le_plus_avance(self):
        v1 = Vehicule("V1", ["R1"])
        v2 = Vehicule("V2", ["R1"])

        self.route.ajouter_vehicule(v1)
        v1.position = 20.0
        self.route.ajouter_vehicule(v2)
        v2.position = 50.0

        assert self.route.tete_de_file() is None

        v2.position = self.route.longueur

        assert self.route.tete_de_file() is v2

    def test_repr(self):
        assert repr(self.route) == "Route(R1, A->B, n=0)"


