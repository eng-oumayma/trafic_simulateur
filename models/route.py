"""Modèle d'une route.

Une route est un tronçon orienté reliant deux intersections. Elle gère la
file des véhicules présents et leur déplacement sans collision.
"""
from __future__ import annotations


class Route:
    """Tronçon routier orienté à une seule voie.

    Attributes:
        ECART_MIN (float): Distance minimale entre deux pare-chocs avant (m).
        nom (str): Nom unique de la route.
        longueur (float): Longueur (m).
        limite_vitesse (float): Vitesse maximale autorisée (km/h).
        origine (str): Identifiant de l'intersection de départ.
        destination (str): Identifiant de l'intersection d'arrivée.
        vehicules (list[Vehicule]): Véhicules actuellement présents.
    """
    ECART_MIN = 7.0  # m entre deux pare-chocs avant (5 m de véhicule + 2 m)

    def __init__(self, nom, longueur, limite_vitesse, origine, destination):
        """Crée une route vide.

        Args:
            nom (str): Nom unique de la route.
            longueur (float): Longueur en mètres (> 0).
            limite_vitesse (float): Limite de vitesse en km/h (> 0).
            origine (str): Identifiant de l'intersection de départ.
            destination (str): Identifiant de l'intersection d'arrivée.

        Raises:
            ValueError: Si la longueur ou la limite de vitesse n'est pas positive.
        """
        if longueur <= 0 or limite_vitesse <= 0:
            raise ValueError("longueur et limite_vitesse doivent être > 0")
        self.nom = nom
        self.longueur = float(longueur)              # m
        self.limite_vitesse = float(limite_vitesse)  # km/h
        self.origine = origine
        self.destination = destination
        self.vehicules = []

    # --- propriétés -----------------------------------------------------
    @property
    def capacite(self):
        """int: Nombre maximal de véhicules que la route peut contenir
        (``longueur // ECART_MIN``, au moins 1).
        """
        return max(1, int(self.longueur // self.ECART_MIN))

    @property
    def taux_occupation(self):
        """float: Rapport entre le nombre de véhicules présents et la capacité,
        compris entre 0 et 1.
        """
        return len(self.vehicules) / self.capacite

    def vitesse_moyenne_kmh(self):
        """Calcule la vitesse instantanée moyenne des véhicules présents.

        Returns:
            float | None: Vitesse moyenne en km/h, ou ``None`` si la route est vide.
        """
        if not self.vehicules:
            return None
        return 3.6 * sum(v.vitesse for v in self.vehicules) / len(self.vehicules)

    # --- gestion des véhicules -----------------------------------------
    def a_de_la_place(self):
        """Indique si un véhicule peut entrer sur la route.

        Il faut que la capacité ne soit pas atteinte et que le dernier véhicule
        entré se soit éloigné d'au moins ``ECART_MIN`` de l'entrée.

        Returns:
            bool: ``True`` si l'entrée est possible.
        """
        if len(self.vehicules) >= self.capacite:
            return False
        return all(v.position >= self.ECART_MIN for v in self.vehicules)

    def ajouter_vehicule(self, vehicule):
        """Place un véhicule au début de la route.

        Args:
            vehicule (Vehicule): Véhicule à ajouter.

        Returns:
            bool: ``True`` si le véhicule a été ajouté, ``False`` si la route est
            saturée à l'entrée.
        """
        if not self.a_de_la_place():
            return False
        vehicule.position = 0.0
        vehicule.route_actuelle = self
        self.vehicules.append(vehicule)
        return True

    def retirer_vehicule(self, vehicule):
        """Retire un véhicule de la route.

        Args:
            vehicule (Vehicule): Véhicule à retirer.

        Raises:
            ValueError: Si le véhicule n'est pas sur cette route.
        """
        self.vehicules.remove(vehicule)
        vehicule.route_actuelle = None

    def vitesse_desiree(self):
        """Calcule la vitesse souhaitée selon le niveau de remplissage.

        Modèle de Greenshields simplifié : la vitesse décroît linéairement de la
        limite (route vide) jusqu'à 5 % de celle-ci (route pleine).

        Returns:
            float: Vitesse cible en m/s.
        """
        v_libre = self.limite_vitesse / 3.6
        return v_libre * max(0.05, 1.0 - self.taux_occupation)

    def mettre_a_jour_vehicules(self, delta_t):
        """Fait avancer tous les véhicules de la route.

        Les véhicules sont traités du plus avancé au moins avancé ; chacun est
        borné par le pare-chocs de celui qui le précède, ce qui interdit tout
        dépassement et toute collision.

        Args:
            delta_t (float): Durée du pas de temps (s).
        """
        v_cible = self.vitesse_desiree()
        limite = self.longueur
        for veh in sorted(self.vehicules, key=lambda v: -v.position):
            veh.avancer(delta_t, v_cible, limite)
            limite = veh.position - self.ECART_MIN

    def tete_de_file(self):
        """Retourne le véhicule arrivé au bout de la route, le cas échéant.

        Returns:
            Vehicule | None: Véhicule en tête s'il a atteint la fin de la route,
            sinon ``None``.
        """
        if not self.vehicules:
            return None
        tete = max(self.vehicules, key=lambda v: v.position)
        return tete if tete.position >= self.longueur - 1e-6 else None

    def __repr__(self):
        """Représentation lisible : nom, sens et nombre de véhicules."""
        return f"Route({self.nom}, {self.origine}->{self.destination}, n={len(self.vehicules)})"
