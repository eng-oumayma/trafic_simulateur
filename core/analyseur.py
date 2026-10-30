"""Calcul des statistiques : vitesses, congestion, temps de parcours."""
from __future__ import annotations
from statistics import mean, median


class Analyseur:
    """Collecte et analyse les données de simulation.

    Attributes:
        historique (list[dict]): Un enregistrement global par tour
            (temps, nombre de véhicules, vitesse moyenne, part d'arrêtés...).
        historique_routes (list[dict]): Un enregistrement par route et par
            tour (occupation, vitesse moyenne, ratio à la limite).
    """
    def __init__(self):
        """Crée un analyseur vide."""
        self.historique = []          # un enregistrement global par tour
        self.historique_routes = []   # un enregistrement par route et par tour
        self._somme_vitesses = 0.0
        self._nb_obs = 0

    def enregistrer(self, temps, reseau):
        """Enregistre l'état du réseau à un instant donné.

        Args:
            temps (float): Temps de simulation (s).
            reseau (ReseauRoutier): Réseau à observer.
        """
        vehs = reseau.vehicules
        vitesses = [v.vitesse * 3.6 for v in vehs]
        self._somme_vitesses += sum(vitesses)
        self._nb_obs += len(vitesses)
        self.historique.append({
            "temps_s": temps,
            "nb_vehicules": len(vehs),
            "nb_termines": len(reseau.termines),
            "vitesse_moyenne_kmh": mean(vitesses) if vitesses else 0.0,
            "part_arretes": (sum(1 for s in vitesses if s < 1.8) / len(vitesses)
                             if vitesses else 0.0),
        })
        for r in reseau.routes.values():
            vm = r.vitesse_moyenne_kmh()
            self.historique_routes.append({
                "temps_s": temps, "route": r.nom, "nb_vehicules": len(r.vehicules),
                "occupation": r.taux_occupation,
                "vitesse_moyenne_kmh": vm if vm is not None else 0.0,
                "ratio_vitesse": (vm / r.limite_vitesse) if vm is not None else 1.0,
            })

    # --- indicateurs ----------------------------------------------------
    def vitesse_moyenne_globale(self):
        """Calcule la vitesse moyenne sur toute la simulation.

        Returns:
            float: Moyenne en km/h de toutes les observations véhicule/tour,
            0 si aucune observation.
        """
        return self._somme_vitesses / self._nb_obs if self._nb_obs else 0.0

    def _par_route(self, cle):
        """Moyenne temporelle d'une colonne de ``historique_routes``.

        Args:
            cle (str): Nom de la colonne.

        Returns:
            dict[str, float]: Moyenne par nom de route.
        """
        acc = {}
        for e in self.historique_routes:
            acc.setdefault(e["route"], []).append(e[cle])
        return {r: mean(vals) for r, vals in acc.items()}

    def occupation_moyenne_par_route(self):
        """Calcule le taux d'occupation moyen de chaque route.

        Returns:
            dict[str, float]: Occupation moyenne (entre 0 et 1) par route.
        """
        return self._par_route("occupation")

    def vitesse_moyenne_par_route(self):
        """Calcule la vitesse moyenne de chaque route, instants vides exclus.

        Returns:
            dict[str, float]: Vitesse moyenne en km/h par route.
        """
        acc = {}
        for e in self.historique_routes:
            if e["nb_vehicules"]:
                acc.setdefault(e["route"], []).append(e["vitesse_moyenne_kmh"])
        return {r: mean(v) for r, v in acc.items()}

    def zones_congestion(self, seuil_ratio=0.35, frequence_min=0.2):
        """Détecte les routes congestionnées.

        Une route est congestionnée à un instant donné si elle contient au moins
        2 véhicules et que leur vitesse moyenne est inférieure à
        ``seuil_ratio`` fois la limite. C'est une zone de congestion si cela
        dure au moins ``frequence_min`` de la simulation.

        Args:
            seuil_ratio (float): Ratio vitesse/limite sous lequel la route est
                jugée congestionnée. Défaut : 0.35.
            frequence_min (float): Fraction minimale du temps en congestion.
                Défaut : 0.2.

        Returns:
            list[dict]: Zones triées par fréquence décroissante, avec les clés
            ``route``, ``frequence``, ``occupation_moyenne`` et
            ``vitesse_moyenne_kmh``.
        """
        total, cong = {}, {}
        for e in self.historique_routes:
            total[e["route"]] = total.get(e["route"], 0) + 1
            if e["nb_vehicules"] >= 2 and e["ratio_vitesse"] < seuil_ratio:
                cong[e["route"]] = cong.get(e["route"], 0) + 1
        occ, vit = self.occupation_moyenne_par_route(), self.vitesse_moyenne_par_route()
        zones = [{"route": r, "frequence": cong[r] / total[r],
                  "occupation_moyenne": occ[r], "vitesse_moyenne_kmh": vit.get(r, 0.0)}
                 for r in cong if cong[r] / total[r] >= frequence_min]
        return sorted(zones, key=lambda z: -z["frequence"])

    @staticmethod
    def temps_parcours(vehicules_termines):
        """Calcule les statistiques de temps de parcours.

        Args:
            vehicules_termines (list[Vehicule]): Véhicules arrivés.

        Returns:
            dict: Clés ``nombre``, ``moyen_s``, ``median_s``, ``min_s`` et
            ``max_s`` (secondes ; 0 si aucun véhicule n'est arrivé).
        """
        t = [v.temps_parcours() for v in vehicules_termines]
        if not t:
            return {"nombre": 0, "moyen_s": 0.0, "median_s": 0.0, "min_s": 0.0, "max_s": 0.0}
        return {"nombre": len(t), "moyen_s": mean(t), "median_s": median(t),
                "min_s": min(t), "max_s": max(t)}

    def resume(self, reseau, duree_s):
        """Produit le résumé final de la simulation.

        Args:
            reseau (ReseauRoutier): Réseau simulé.
            duree_s (float): Durée simulée (s).

        Returns:
            dict: Résumé sérialisable en JSON (véhicules créés/arrivés, vitesse
            globale, temps de parcours, zones de congestion).
        """
        return {
            "duree_simulee_min": duree_s / 60,
            "vehicules_crees": reseau.nb_crees,
            "vehicules_arrives": len(reseau.termines),
            "vehicules_en_circulation": len(reseau.vehicules),
            "vitesse_moyenne_globale_kmh": self.vitesse_moyenne_globale(),
            "temps_parcours": self.temps_parcours(reseau.termines),
            "zones_congestion": self.zones_congestion(),
        }
