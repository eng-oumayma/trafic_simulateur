# Rapport de tests — Simulateur de trafic

## Synthèse

Le dossier `tests/` contient actuellement **61 cas de test** : 25 fonctions de
test dans `test_route.py` (dont un test paramétré en cinq cas), 14 dans
`test_simulateur.py` et 18 dans `test_vehicule.py`.

Les sorties terminal complètes de la dernière exécution ne sont pas disponibles
dans les fichiers du projet. Le cache `.pytest_cache` est donc le seul indice
historique consultable ; il ne permet pas de certifier le nombre de tests
effectivement exécutés ni le nombre de réussites.

| Indicateur | Résultat disponible | Commentaire |
|---|---:|---|
| Cas de test dans le code actuel | 61 | Comptage statique des tests, paramètres compris |
| Tests exécutés lors de la dernière commande | Non vérifiable | La sortie de terminal n’est pas présente |
| Tests réussis | Non vérifiable | Le cache ne fournit pas un bilan de réussite fiable |
| Échecs enregistrés dans le cache | 1 | `tests/test_route.py::test_vitesse_moyenne` |
| Identifiants de tests conservés dans le cache | 62 | Comprend un identifiant qui n’existe plus dans le code actuel |

**Conclusion sur les résultats :** le cache garde la trace d’un échec associé à
`tests/test_route.py::test_vitesse_moyenne`, mais cet identifiant est obsolète :
le test présent dans le code se nomme
`TestRoute::test_vitesse_moyenne`. Sans la sortie de la commande concernée ou
une nouvelle exécution, il est impossible de confirmer si cet échec correspond
à un défaut toujours présent. Les 61 autres tests ne peuvent pas être déclarés
réussis sur la seule base du cache.

## Anomalies détectées et corrections

| Anomalie | État / correction |
|---|---|
| Le cache pytest conserve un échec pour `test_route.py::test_vitesse_moyenne`. | Anomalie historique à vérifier : le cache ne contient ni traceback ni cause détaillée. Aucune correction de code n’est documentée. |
| Le cache contient 62 identifiants, alors que les fichiers de test actuels définissent 61 cas ; l’identifiant supplémentaire est `tests/test_route.py::test_vitesse_moyenne`. | Cache probablement périmé par rapport aux noms actuels. Aucune correction du cache ni du code n’a été effectuée. |
| Les sorties terminal complètes ne sont pas disponibles. | Le bilan succès/échecs de la dernière exécution reste à confirmer à partir de ces sorties ou d’un nouveau lancement de pytest. |

**Corrections effectuées pour ce rapport :** aucune correction du simulateur ou
des tests. Seul ce rapport a été créé ; les anomalies ci-dessus sont consignées
sans prétendre qu’elles ont été corrigées.
