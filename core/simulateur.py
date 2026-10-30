"""Simulateur : charge la configuration et pilote la boucle temporelle."""
from __future__ import annotations
import json
import math
import random

from models.reseau import ReseauRoutier
from core.analyseur import Analyseur
from out import affichage, export
from pathlib import Path

from exceptions import ConfigurationError

class Simulateur:
    """Orchestrateur de la simulation.

    Exemple:
        >>> simu = Simulateur(fichier_config="data/config_reseau.json")
        >>> resume = simu.lancer_simulation(n_tours=60, delta_t=60)

    Attributes:
        config (dict): Configuration chargée.
        reseau (ReseauRoutier): Réseau simulé.
        analyseur (Analyseur): Collecteur de statistiques.
        rng (random.Random): Générateur pseudo-aléatoire (graine ``seed``).
        taux_apparition (float): Véhicules créés par minute.
        sous_pas (float): Durée maximale d'un sous-pas de calcul (s).
        temps (float): Temps de simulation courant (s).
        resume (dict | None): Résumé final, disponible après la simulation.
    """
    def __init__(self, fichier_config=None, config=None, afficher=True,
                 dossier_sortie="out/resultats"):
        """Initialise le simulateur.

        Args:
            fichier_config (str | None): Chemin d'un fichier JSON de configuration.
            config (dict | None): Configuration déjà chargée (prioritaire).
            afficher (bool): Affiche l'état et le rapport en console.
            dossier_sortie (str): Dossier des exports et graphiques.

        Raises:
            ValueError: Si ni ``fichier_config`` ni ``config`` n'est fourni.
        """
        if config is None:
            if fichier_config is None:
                raise ValueError("Fournir fichier_config ou config")
            with open(fichier_config, encoding="utf-8") as f:
                config = json.load(f)
        gen = config.get("generation", {})
        self.config = config
        self.reseau = ReseauRoutier.from_dict(config)
        self.analyseur = Analyseur()
        self.rng = random.Random(gen.get("seed"))
        self.vehicules_initiaux = gen.get("vehicules_initiaux", 0)
        self.taux_apparition = gen.get("taux_apparition", 0.0)  # véhicules/min
        self.sous_pas = gen.get("sous_pas", 5)                  # s
        self.afficher = afficher
        self.dossier_sortie = dossier_sortie
        self.temps = 0.0
        self.resume = None

    def _generer(self, duree):
        """Fait apparaître des véhicules sur la durée donnée.

        Le nombre attendu est ``taux_apparition * duree / 60`` ; sa partie
        fractionnaire est tirée au sort.

        Args:
            duree (float): Durée écoulée (s).
        """
        attendu = self.taux_apparition * duree / 60
        n = int(attendu) + (1 if self.rng.random() < attendu - int(attendu) else 0)
        for _ in range(n):
            self.reseau.generer_vehicule(self.rng, self.temps)

    def lancer_simulation(self, n_tours, delta_t, intervalle_affichage=10,
                          exporter=True, graphiques=True):
        """Lance la simulation.

        Chaque tour de ``delta_t`` secondes est découpé en sous-pas d'au plus
        ``sous_pas`` secondes, pendant lesquels des véhicules apparaissent et le
        réseau est mis à jour. Les statistiques sont enregistrées à chaque tour.

        Args:
            n_tours (int): Nombre de tours.
            delta_t (float): Durée d'un tour (s).
            intervalle_affichage (int): Affiche l'état tous les N tours.
            exporter (bool): Exporte les résultats en CSV/JSON.
            graphiques (bool): Génère les graphiques PNG.

        Returns:
            dict: Résumé de la simulation (voir :meth:`Analyseur.resume`).
        """

        if not isinstance(nombre_iterations, int) or isinstance(nombre_iterations, bool):
            raise ValueError("Le nombre d'itérations doit être un entier.")

        if nombre_iterations <= 0:
            raise ValueError("Le nombre d'itérations doit être positif.")

        chemin = Path(self.fichier_config)

        try:
            with chemin.open("r", encoding="utf-8") as fichier:
                configuration = json.load(fichier)

        except FileNotFoundError as erreur:
            raise ConfigurationError(
                f"Fichier de configuration introuvable : {chemin}"
            ) from erreur

        except json.JSONDecodeError as erreur:
            raise ConfigurationError(
                "Le fichier de configuration contient un JSON invalide."
            ) from erreur




        for _ in range(self.vehicules_initiaux):
            self.reseau.generer_vehicule(self.rng, self.temps,
                                         candidates=list(self.reseau.routes))
        n_sous = max(1, math.ceil(delta_t / self.sous_pas))
        h = delta_t / n_sous

        for tour in range(n_tours):
            for k in range(n_sous):
                self._generer(h)
                self.reseau.mettre_a_jour(h, self.temps + k * h)
            self.temps += delta_t
            self.analyseur.enregistrer(self.temps, self.reseau)
            if self.afficher and (tour % intervalle_affichage == 0 or tour == n_tours - 1):
                affichage.afficher_etat_console(self.temps, self.reseau, self.analyseur)

        self.resume = self.analyseur.resume(self.reseau, self.temps)
        if self.afficher:
            affichage.afficher_resume(self.resume)
        if exporter:
            export.exporter_tout(self, self.dossier_sortie)
        if graphiques:
            affichage.tracer_tout(self, self.dossier_sortie)
        return self.resume
