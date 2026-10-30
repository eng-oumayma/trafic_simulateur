"""Modèle d'un véhicule.

Toutes les grandeurs sont exprimées en unités SI : mètres, secondes et m/s
(sauf mention contraire).
"""
from __future__ import annotations


class Vehicule:
    """Véhicule circulant sur le réseau.

    Un véhicule suit un itinéraire (liste ordonnée de noms de routes) et se trouve
    à tout instant sur une route à une certaine position.

    Attributes:
        LONGUEUR (float): Longueur d'un véhicule en mètres.
        identifiant (str): Identifiant unique du véhicule.
        itineraire (list[str]): Noms des routes à emprunter, dans l'ordre.
        index_route (int): Indice, dans l'itinéraire, de la route actuelle.
        route_actuelle (Route | None): Route sur laquelle se trouve le véhicule.
        position (float): Distance parcourue depuis le début de la route (m).
        vitesse (float): Vitesse instantanée (m/s).
        temps_creation (float): Instant d'apparition (s).
        temps_arrivee (float | None): Instant d'arrivée à destination (s).
        distance_parcourue (float): Distance totale parcourue (m).
        temps_arret (float): Temps cumulé passé à l'arrêt (s).
        arrive (bool): ``True`` une fois la destination atteinte.
    """
    LONGUEUR = 5.0  # m

    def __init__(self, identifiant, itineraire, temps_creation=0.0):
        """Crée un véhicule non encore placé sur une route.

        Args:
            identifiant (str): Identifiant unique.
            itineraire (list[str]): Noms des routes à emprunter, dans l'ordre.
            temps_creation (float): Instant de création en secondes. Défaut : 0.
        """
        self.identifiant = identifiant
        self.itineraire = list(itineraire)   # noms de routes à emprunter
        self.index_route = 0                 # position dans l'itinéraire
        self.route_actuelle = None           # objet Route
        self.position = 0.0                  # m depuis le début de la route
        self.vitesse = 0.0                   # m/s
        self.temps_creation = temps_creation
        self.temps_arrivee = None
        self.distance_parcourue = 0.0
        self.temps_arret = 0.0               # secondes passées à l'arrêt
        self.arrive = False

    # ------------------------------------------------------------------
    def avancer(self, delta_t, vitesse_cible, limite_position):
        """Fait avancer le véhicule pendant ``delta_t`` secondes.

        Le déplacement est borné par ``limite_position`` (fin de route ou pare-chocs
        du véhicule qui précède) ; le véhicule ne recule jamais. La vitesse
        instantanée est mise à jour, et le temps d'arrêt cumulé augmente si elle
        est inférieure à 0,5 m/s.

        Args:
            delta_t (float): Durée du pas de temps (s), strictement positive.
            vitesse_cible (float): Vitesse souhaitée (m/s).
            limite_position (float): Position maximale autorisée sur la route (m).
        """
        if delta_t <= 0:
            raise ValueError("delta_t doit être strictement positif.")

        if vitesse_cible < 0:
            raise ValueError("La vitesse ne peut pas être négative.")

        if limite_position < 0:
            raise ValueError("La limite de position ne peut pas être négative.")

        try:
            nouvelle_position = self.position + vitesse_cible * delta_t
            self.position = min(nouvelle_position, limite_position)

        except (TypeError, AttributeError) as erreur:
            raise ValueError(
                "Impossible de mettre à jour la position du véhicule."
            ) from erreur


    def route_suivante(self):
        """Donne la prochaine route de l'itinéraire.

        Returns:
            str | None: Nom de la route suivante, ou ``None`` si le véhicule est
            sur la dernière route de son itinéraire.
        """
        if self.index_route + 1 < len(self.itineraire):
            return self.itineraire[self.index_route + 1]
        return None

    def changer_de_route(self, nouvelle_route):
        """Fait passer le véhicule sur une nouvelle route.

        Le véhicule est retiré de sa route actuelle, placé au début de
        ``nouvelle_route`` et son index d'itinéraire est incrémenté. Rien n'est
        modifié si la nouvelle route n'a pas de place à l'entrée.

        Args:
            nouvelle_route (Route): Route de destination.

        Returns:
            bool: ``True`` si le changement a eu lieu, ``False`` si la route est
            saturée.
        """
        if not nouvelle_route.a_de_la_place():
            return False
        if self.route_actuelle is not None:
            self.route_actuelle.retirer_vehicule(self)
        nouvelle_route.ajouter_vehicule(self)
        self.index_route += 1
        return True

    def temps_parcours(self):
        """Calcule la durée totale du trajet.

        Returns:
            float | None: Temps de parcours en secondes, ou ``None`` si le
            véhicule n'est pas encore arrivé.
        """
        if self.temps_arrivee is None:
            return None
        return self.temps_arrivee - self.temps_creation

    def __repr__(self):
        """Représentation lisible : identifiant, route et position."""
        r = self.route_actuelle.nom if self.route_actuelle else None
        return f"Vehicule({self.identifiant}, route={r}, pos={self.position:.0f}m)"
