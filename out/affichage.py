"""Affichage console et graphiques (matplotlib)."""
from __future__ import annotations
import os
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.patches import FancyArrowPatch


# ---------------------------------------------------------------- console
def afficher_etat_console(temps, reseau, analyseur):
    """Affiche une ligne d'état de la simulation.

    Args:
        temps (float): Temps de simulation (s).
        reseau (ReseauRoutier): Réseau simulé.
        analyseur (Analyseur): Source de la dernière mesure.
    """
    h = analyseur.historique[-1]
    print(f"[t={temps / 60:6.1f} min] en circulation: {h['nb_vehicules']:4d} | "
          f"arrivés: {h['nb_termines']:4d} | vitesse moy.: {h['vitesse_moyenne_kmh']:5.1f} km/h | "
          f"à l'arrêt: {h['part_arretes'] * 100:4.1f} %")


def afficher_resume(resume):
    """Affiche le rapport final en console.

    Args:
        resume (dict): Résumé produit par :meth:`Analyseur.resume`.
    """
    tp = resume["temps_parcours"]
    print("\n" + "=" * 62 + "\n RAPPORT DE SIMULATION\n" + "=" * 62)
    print(f" Durée simulée            : {resume['duree_simulee_min']:.0f} min")
    print(f" Véhicules créés / arrivés: {resume['vehicules_crees']} / {resume['vehicules_arrives']}")
    print(f" Encore en circulation    : {resume['vehicules_en_circulation']}")
    print(f" Vitesse moyenne globale  : {resume['vitesse_moyenne_globale_kmh']:.1f} km/h")
    if tp["nombre"]:
        print(f" Temps de parcours        : moy {tp['moyen_s'] / 60:.1f} min, "
              f"méd {tp['median_s'] / 60:.1f}, min {tp['min_s'] / 60:.1f}, max {tp['max_s'] / 60:.1f}")
    zones = resume["zones_congestion"]
    print(" Zones de congestion      :", "aucune" if not zones else "")
    for z in zones:
        print(f"   - {z['route']:<6} congestionnée {z['frequence'] * 100:4.0f} % du temps | "
              f"occupation {z['occupation_moyenne'] * 100:4.0f} % | "
              f"{z['vitesse_moyenne_kmh']:4.1f} km/h")
    print("=" * 62)


# ---------------------------------------------------------------- graphiques
def _finir(fig, chemin, montrer):
    """Enregistre et/ou affiche une figure, puis la ferme.

    Args:
        fig (matplotlib.figure.Figure): Figure à finaliser.
        chemin (str | None): Fichier image de sortie.
        montrer (bool): Ouvre une fenêtre interactive.
    """
    fig.tight_layout()
    if chemin:
        fig.savefig(chemin, dpi=130)
    if montrer:
        plt.show()
    plt.close(fig)


def tracer_evolution(analyseur, chemin=None, montrer=False):
    """Trace la vitesse moyenne et le nombre de véhicules au cours du temps.

    Args:
        analyseur (Analyseur): Source des données.
        chemin (str | None): Fichier image de sortie.
        montrer (bool): Ouvre une fenêtre interactive.
    """
    t = [h["temps_s"] / 60 for h in analyseur.historique]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    a1.plot(t, [h["vitesse_moyenne_kmh"] for h in analyseur.historique], color="tab:blue")
    a1.set_ylabel("Vitesse moyenne (km/h)")
    a1.set_title("Évolution du trafic")
    a2.plot(t, [h["nb_vehicules"] for h in analyseur.historique], label="en circulation")
    a2.plot(t, [h["nb_termines"] for h in analyseur.historique], label="arrivés")
    a2.set_xlabel("Temps (min)")
    a2.set_ylabel("Véhicules")
    a2.legend()
    for a in (a1, a2):
        a.grid(alpha=.3)
    _finir(fig, chemin, montrer)


def tracer_congestion(analyseur, chemin=None, montrer=False):
    """Trace l'occupation moyenne de chaque route (histogramme trié).

    Args:
        analyseur (Analyseur): Source des données.
        chemin (str | None): Fichier image de sortie.
        montrer (bool): Ouvre une fenêtre interactive.
    """
    occ = analyseur.occupation_moyenne_par_route()
    noms = sorted(occ, key=occ.get, reverse=True)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(noms, [occ[n] * 100 for n in noms],
           color=[cm.RdYlGn_r(min(1, occ[n] * 2)) for n in noms])
    ax.set_ylabel("Occupation moyenne (%)")
    ax.set_title("Occupation moyenne par route")
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right")
    _finir(fig, chemin, montrer)


def tracer_temps_parcours(reseau, chemin=None, montrer=False):
    """Trace l'histogramme des temps de parcours.

    Args:
        reseau (ReseauRoutier): Réseau simulé.
        chemin (str | None): Fichier image de sortie.
        montrer (bool): Ouvre une fenêtre interactive.
    """
    t = [v.temps_parcours() / 60 for v in reseau.termines]
    fig, ax = plt.subplots(figsize=(7, 4))
    if t:
        ax.hist(t, bins=min(20, max(5, len(t) // 3)), color="tab:purple", edgecolor="white")
    ax.set_xlabel("Temps de parcours (min)")
    ax.set_ylabel("Nombre de véhicules")
    ax.set_title("Distribution des temps de parcours")
    _finir(fig, chemin, montrer)


def tracer_carte(reseau, valeurs, chemin=None, montrer=False, titre="Carte de congestion"):
    """Dessine la carte du réseau, colorée selon une valeur par route.

    Les intersections à feux sont des carrés, les autres des cercles. Les
    routes à double sens sont décalées pour rester distinctes.

    Args:
        reseau (ReseauRoutier): Réseau à dessiner.
        valeurs (dict[str, float]): Occupation moyenne par nom de route.
        chemin (str | None): Fichier image de sortie.
        montrer (bool): Ouvre une fenêtre interactive.
        titre (str): Titre de la carte.
    """
    xs = [i.x for i in reseau.intersections.values()]
    ys = [i.y for i in reseau.intersections.values()]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
    decal, raccourci = 0.025 * span, 0.06 * span
    norm = colors.Normalize(0, 1)
    fig, ax = plt.subplots(figsize=(8, 6))
    for r in reseau.routes.values():
        a, b = reseau.intersections[r.origine], reseau.intersections[r.destination]
        dx, dy = b.x - a.x, b.y - a.y
        n = (dx * dx + dy * dy) ** 0.5 or 1.0
        ux, uy, nx, ny = dx / n, dy / n, -dy / n, dx / n
        p1 = (a.x + ux * raccourci + nx * decal, a.y + uy * raccourci + ny * decal)
        p2 = (b.x - ux * raccourci + nx * decal, b.y - uy * raccourci + ny * decal)
        couleur = cm.RdYlGn_r(norm(min(1.0, 2 * valeurs.get(r.nom, 0.0))))
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                                     lw=3, color=couleur))
    for i in reseau.intersections.values():
        ax.scatter(i.x, i.y, s=330, marker="s" if i.a_des_feux else "o",
                   color="white", edgecolor="black", zorder=3)
        ax.annotate(i.identifiant, (i.x, i.y), ha="center", va="center", zorder=4, fontsize=9)
    ax.set_xlim(min(xs) - .15 * span, max(xs) + .15 * span)
    ax.set_ylim(min(ys) - .15 * span, max(ys) + .15 * span)
    ax.set_aspect("equal")
    ax.set_title(titre + "  (carré = feux tricolores)")
    sm = cm.ScalarMappable(norm=colors.Normalize(0, .5), cmap=cm.RdYlGn_r)
    fig.colorbar(sm, ax=ax, label="Occupation moyenne", shrink=.8)
    ax.axis("off")
    _finir(fig, chemin, montrer)


def tracer_tout(simu, dossier):
    """Génère les quatre graphiques standard dans un dossier.

    Crée ``evolution.png``, ``congestion.png``, ``temps_parcours.png`` et
    ``carte.png``.

    Args:
        simu (Simulateur): Simulation terminée.
        dossier (str): Dossier de sortie.
    """
    os.makedirs(dossier, exist_ok=True)
    tracer_evolution(simu.analyseur, os.path.join(dossier, "evolution.png"))
    tracer_congestion(simu.analyseur, os.path.join(dossier, "congestion.png"))
    tracer_temps_parcours(simu.reseau, os.path.join(dossier, "temps_parcours.png"))
    tracer_carte(simu.reseau, simu.analyseur.occupation_moyenne_par_route(),
                 os.path.join(dossier, "carte.png"))
