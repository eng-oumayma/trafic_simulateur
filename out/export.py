"""Export des résultats de simulation en CSV et JSON."""
from __future__ import annotations
import csv
import json
import os


def _csv(chemin, lignes, colonnes):
    """Écrit une liste de dictionnaires dans un fichier CSV.

    Args:
        chemin (str): Fichier de sortie.
        lignes (list[dict]): Lignes à écrire.
        colonnes (list[str]): Noms et ordre des colonnes.
    """
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colonnes)
        w.writeheader()
        w.writerows(lignes)


def exporter_historique_csv(analyseur, chemin):
    """Exporte l'évolution globale du trafic.

    Args:
        analyseur (Analyseur): Source des données.
        chemin (str): Fichier CSV de sortie.
    """
    _csv(chemin, analyseur.historique,
         ["temps_s", "nb_vehicules", "nb_termines", "vitesse_moyenne_kmh", "part_arretes"])


def exporter_routes_csv(analyseur, chemin):
    """Exporte les mesures par route et par tour.

    Args:
        analyseur (Analyseur): Source des données.
        chemin (str): Fichier CSV de sortie.
    """
    _csv(chemin, analyseur.historique_routes,
         ["temps_s", "route", "nb_vehicules", "occupation",
          "vitesse_moyenne_kmh", "ratio_vitesse"])


def exporter_trajets_csv(reseau, chemin):
    """Exporte les trajets des véhicules arrivés à destination.

    Args:
        reseau (ReseauRoutier): Réseau simulé.
        chemin (str): Fichier CSV de sortie.
    """
    lignes = [{"id": v.identifiant, "itineraire": ">".join(v.itineraire),
               "temps_creation_s": v.temps_creation, "temps_arrivee_s": v.temps_arrivee,
               "temps_parcours_s": v.temps_parcours(), "distance_m": round(v.distance_parcourue, 1),
               "temps_arret_s": v.temps_arret} for v in reseau.termines]
    _csv(chemin, lignes, ["id", "itineraire", "temps_creation_s", "temps_arrivee_s",
                          "temps_parcours_s", "distance_m", "temps_arret_s"])


def exporter_resume_json(resume, chemin):
    """Exporte le résumé de la simulation.

    Args:
        resume (dict): Résumé produit par :meth:`Analyseur.resume`.
        chemin (str): Fichier JSON de sortie.
    """
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(resume, f, indent=2, ensure_ascii=False)


def exporter_tout(simu, dossier):
    """Exporte tous les fichiers de résultats dans un dossier.

    Crée ``historique.csv``, ``routes.csv``, ``trajets.csv`` et
    ``resume.json``. Le dossier est créé s'il n'existe pas.

    Args:
        simu (Simulateur): Simulation terminée.
        dossier (str): Dossier de sortie.
    """
    os.makedirs(dossier, exist_ok=True)
    exporter_historique_csv(simu.analyseur, os.path.join(dossier, "historique.csv"))
    exporter_routes_csv(simu.analyseur, os.path.join(dossier, "routes.csv"))
    exporter_trajets_csv(simu.reseau, os.path.join(dossier, "trajets.csv"))
    exporter_resume_json(simu.resume, os.path.join(dossier, "resume.json"))
