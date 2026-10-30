"""Interface en ligne de commande du simulateur (``simulateur-trafic``)."""
from __future__ import annotations

import argparse

from core import __version__
from core.simulateur import Simulateur


def construire_parseur():
    """
    Construit le parseur d'arguments.

    Returns:
        argparse.ArgumentParser: Parseur configuré.
    """
    p = argparse.ArgumentParser(
        prog="simulateur-trafic",
        description="Simulateur de trafic routier.")
    p.add_argument("-c", "--config", default="data/config_reseau.json",
                   help="fichier JSON du réseau (défaut : %(default)s)")
    p.add_argument("-n", "--tours", type=int, default=60,
                   help="nombre de tours (défaut : %(default)s)")
    p.add_argument("-d", "--delta-t", type=float, default=60,
                   help="durée d'un tour en secondes (défaut : %(default)s)")
    p.add_argument("-o", "--sortie", default="out/resultats",
                   help="dossier des résultats (défaut : %(default)s)")
    p.add_argument("--silencieux", action="store_true",
                   help="n'affiche rien en console")
    p.add_argument("--sans-graphiques", action="store_true",
                   help="ne génère pas les images")
    p.add_argument("-V", "--version", action="version",
                   version=f"%(prog)s {__version__}")
    return p


def main(argv=None):
    """
    Point d'entrée de la commande ``simulateur-trafic``.

    Args:
        argv (list[str] | None): Arguments ; ``sys.argv`` par défaut.

    Returns:
        int: Code de sortie (0 si tout s'est bien passé).
    """
    args = construire_parseur().parse_args(argv)
    simu = Simulateur(fichier_config=args.config, afficher=not args.silencieux,
                      dossier_sortie=args.sortie)
    simu.lancer_simulation(args.tours, args.delta_t,
                           graphiques=not args.sans_graphiques)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
