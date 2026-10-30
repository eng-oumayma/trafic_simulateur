"""Réseau routier : routes, intersections (avec feux) et logique globale.

Le réseau est un graphe orienté dont les nœuds sont des
:class:`Intersection` et les arêtes des :class:`~models.route.Route`.
Il est généralement construit à partir d'un fichier JSON
(:meth:`ReseauRoutier.from_json`).
"""
from __future__ import annotations
import json
from collections import deque

from .route import Route
from .vehicule import Vehicule


class Intersection:
    """Nœud du réseau, éventuellement régulé par des feux tricolores.

    Les feux fonctionnent par phases : pendant une phase, seules les routes
    entrantes listées sont au vert. Sans phases, l'intersection est libre.

    Attributes:
        identifiant (str): Identifiant unique.
        x (float): Abscisse (pour la cartographie).
        y (float): Ordonnée (pour la cartographie).
        phases (list[tuple[frozenset[str], float]]): Couples
            (routes au vert, durée en secondes).
    """

    def __init__(self, identifiant, x=0.0, y=0.0, phases=None):
        """Crée une intersection.

        Args:
            identifiant (str): Identifiant unique.
            x (float): Abscisse. Défaut : 0.
            y (float): Ordonnée. Défaut : 0.
            phases (list[dict] | None): Phases de feux, chaque phase étant un
                dictionnaire ``{"routes": [...], "duree": secondes}``.
        """
        self.identifiant = identifiant
        self.x, self.y = float(x), float(y)
        self.phases = [(frozenset(p["routes"]), float(p["duree"]))
                       for p in (phases or [])]

    @property
    def cycle(self):
        """float: Durée totale d'un cycle de feux (s), 0 sans feux."""
        return sum(d for _, d in self.phases)

    @property
    def a_des_feux(self):
        """bool: ``True`` si l'intersection est régulée par des feux."""
        return bool(self.phases)

    def est_vert(self, nom_route, temps):
        """Indique si une route entrante peut passer à l'instant donné.

        Args:
            nom_route (str): Nom de la route entrante.
            temps (float): Temps de simulation (s).

        Returns:
            bool: ``True`` si le feu est vert, ou si la route n'est concernée
            par aucune phase (passage libre).
        """
        if not self.phases or not any(nom_route in r for r, _ in self.phases):
            return True
        t = temps % self.cycle
        cumul = 0.0
        for routes, duree in self.phases:
            if t < cumul + duree:
                return nom_route in routes
            cumul += duree
        return False


class ReseauRoutier:
    """Ensemble des routes et intersections, et dynamique globale du trafic.

    Attributes:
        routes (dict[str, Route]): Routes indexées par nom.
        intersections (dict[str, Intersection]): Intersections indexées par id.
        points_entree (list[str]): Routes où apparaissent les véhicules
            (toutes les routes si la liste est vide).
        termines (list[Vehicule]): Véhicules arrivés à destination.
        nb_crees (int): Nombre total de véhicules créés.
    """
    def __init__(self, points_entree=None):
        """Crée un réseau vide.

        Args:
            points_entree (list[str] | None): Noms des routes d'entrée.
        """
        self.routes = {}
        self.intersections = {}
        self.points_entree = list(points_entree or [])
        self.termines = []      # véhicules arrivés à destination
        self.nb_crees = 0
        self._succ = None       # cache du graphe route -> routes suivantes

    # --- construction ---------------------------------------------------
    @classmethod
    def from_dict(cls, config):
        """Construit un réseau à partir d'un dictionnaire de configuration.

        Args:
            config (dict): Dictionnaire avec les clés ``intersections``,
                ``routes`` et, optionnellement, ``generation``.

        Returns:
            ReseauRoutier: Réseau construit.

        Raises:
            ValueError: Si une route est dupliquée ou si un point d'entrée est
                inconnu.
            KeyError: Si une clé obligatoire est absente.
        """
        reseau = cls(config.get("generation", {}).get("points_entree"))
        for i in config["intersections"]:
            reseau.ajouter_intersection(
                Intersection(i["id"], i.get("x", 0), i.get("y", 0), i.get("feux")))
        for r in config["routes"]:
            reseau.ajouter_route(Route(r["nom"], r["longueur"], r["limite_vitesse"],
                                       r["origine"], r["destination"]))
        for nom in reseau.points_entree:
            if nom not in reseau.routes:
                raise ValueError(f"Point d'entrée inconnu : {nom}")
        return reseau

    @classmethod
    def from_json(cls, chemin):
        """Construit un réseau à partir d'un fichier JSON.

        Args:
            chemin (str): Chemin du fichier de configuration.

        Returns:
            ReseauRoutier: Réseau construit.
        """
        with open(chemin, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def ajouter_intersection(self, inter):
        """Ajoute (ou remplace) une intersection.

        Args:
            inter (Intersection): Intersection à ajouter.
        """
        self.intersections[inter.identifiant] = inter

    def ajouter_route(self, route):
        """Ajoute une route, en créant ses intersections si nécessaire.

        Args:
            route (Route): Route à ajouter.

        Raises:
            ValueError: Si une route de même nom existe déjà.
        """
        if route.nom in self.routes:
            raise ValueError(f"Route dupliquée : {route.nom}")
        for n in (route.origine, route.destination):
            if n not in self.intersections:
                self.ajouter_intersection(Intersection(n))
        self.routes[route.nom] = route
        self._succ = None

    # --- graphe ---------------------------------------------------------
    def routes_suivantes(self, nom_route):
        """Liste les routes qu'un véhicule peut emprunter après une route donnée.

        Les demi-tours sont exclus. Le graphe est mis en cache.

        Args:
            nom_route (str): Nom de la route actuelle.

        Returns:
            list[str]: Noms des routes accessibles.
        """
        if self._succ is None:
            self._succ = {}
            for r in self.routes.values():
                self._succ[r.nom] = [s.nom for s in self.routes.values()
                                     if s.origine == r.destination
                                     and s.destination != r.origine]  # pas de demi-tour
        return self._succ[nom_route]

    def itineraire_aleatoire(self, rng, depart):
        """Choisit une destination au hasard et calcule le plus court chemin.

        Le calcul est un parcours en largeur (BFS) sur le graphe des routes.

        Args:
            rng (random.Random): Générateur pseudo-aléatoire.
            depart (str): Nom de la route de départ.

        Returns:
            list[str]: Itinéraire, du départ à la destination incluse. Réduit à
            ``[depart]`` si aucune autre route n'est atteignable.
        """
        parents, file = {depart: None}, deque([depart])
        while file:
            courant = file.popleft()
            for s in self.routes_suivantes(courant):
                if s not in parents:
                    parents[s] = courant
                    file.append(s)
        cibles = [n for n in parents if n != depart]
        if not cibles:
            return [depart]
        n, chemin = rng.choice(sorted(cibles)), []
        while n is not None:
            chemin.append(n)
            n = parents[n]
        return chemin[::-1]

    # --- véhicules ------------------------------------------------------
    @property
    def vehicules(self):
        """list[Vehicule]: Tous les véhicules actuellement en circulation."""
        return [v for r in self.routes.values() for v in r.vehicules]

    def generer_vehicule(self, rng, temps, candidates=None):
        """Crée un véhicule sur une route d'entrée tirée au hasard.

        Args:
            rng (random.Random): Générateur pseudo-aléatoire.
            temps (float): Temps de simulation courant (s).
            candidates (list[str] | None): Routes candidates ; par défaut les
                points d'entrée, ou toutes les routes s'il n'y en a pas.

        Returns:
            Vehicule | None: Véhicule créé, ou ``None`` si la route choisie est
            saturée à l'entrée.
        """
        noms = sorted(candidates or self.points_entree or self.routes)
        depart = self.routes[rng.choice(noms)]
        if not depart.a_de_la_place():
            return None
        v = Vehicule(f"V{self.nb_crees + 1:05d}",
                     self.itineraire_aleatoire(rng, depart.nom), temps)
        depart.ajouter_vehicule(v)
        self.nb_crees += 1
        return v

    # --- dynamique ------------------------------------------------------
    def mettre_a_jour(self, delta_t, temps):
        """Exécute un pas de simulation.

        Étape 1 : chaque route fait avancer ses véhicules. Étape 2 : le véhicule
        en tête de chaque route sort du réseau s'il est arrivé, ou passe sur la
        route suivante si le feu est vert et qu'il y a de la place.

        Args:
            delta_t (float): Durée du pas (s).
            temps (float): Temps de simulation au début du pas (s).
        """
        for route in self.routes.values():
            route.mettre_a_jour_vehicules(delta_t)

        for route in self.routes.values():
            tete = route.tete_de_file()
            if tete is None:
                continue
            suivante = tete.route_suivante()
            if suivante is None:                      # destination atteinte
                route.retirer_vehicule(tete)
                tete.arrive, tete.temps_arrivee = True, temps + delta_t
                self.termines.append(tete)
                continue
            inter = self.intersections[route.destination]
            if inter.est_vert(route.nom, temps):
                tete.changer_de_route(self.routes[suivante])  # False si saturée
