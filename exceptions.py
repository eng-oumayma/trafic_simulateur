
class SimulateurError(Exception):
    """Exception de base du simulateur."""


class RoutePleineError(SimulateurError):
    """Levée lorsqu'une route ne peut plus accueillir de véhicule."""


class VehiculeDejaPresentError(SimulateurError):
    """Levée lorsqu'un véhicule est déjà présent sur une route."""


class RouteIntrouvableError(SimulateurError):
    """Levée lorsqu'une route demandée n'existe pas."""


class ConfigurationError(SimulateurError):
    """Levée lorsqu'un fichier de configuration est invalide."""
