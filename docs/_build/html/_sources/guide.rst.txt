Guide d'utilisation
===================

Installation
------------

.. code-block:: bash

   pip install -r requirements.txt

Lancer une simulation
---------------------

.. code-block:: python

   from core.simulateur import Simulateur

   simu = Simulateur(fichier_config="data/config_reseau.json")
   resume = simu.lancer_simulation(n_tours=60, delta_t=60)  # 60 min, pas de 1 min

Les résultats sont écrits dans ``out/resultats/`` : ``historique.csv``,
``routes.csv``, ``trajets.csv``, ``resume.json`` et quatre graphiques PNG.

Format de ``config_reseau.json``
--------------------------------

.. code-block:: json

   {
     "intersections": [
       {"id": "B", "x": 1.5, "y": 0,
        "feux": [{"routes": ["A-B"], "duree": 30},
                 {"routes": ["E-B"], "duree": 30}]}
     ],
     "routes": [
       {"nom": "A-B", "origine": "A", "destination": "B",
        "longueur": 1500, "limite_vitesse": 70}
     ],
     "generation": {
       "seed": 42,
       "vehicules_initiaux": 30,
       "taux_apparition": 18,
       "points_entree": ["A-B"],
       "sous_pas": 5
     }
   }

``longueur`` est en mètres, ``limite_vitesse`` en km/h, ``duree`` en
secondes et ``taux_apparition`` en véhicules par minute.

Architecture
------------

.. code-block:: text

   main.py ─► core.Simulateur ─► models.ReseauRoutier ─► models.Route ─► models.Vehicule
                   │
                   ├─► core.Analyseur   (statistiques)
                   └─► out.affichage / out.export  (rapports)

Tests
-----

.. code-block:: bash

   python -m unittest discover -s tests
