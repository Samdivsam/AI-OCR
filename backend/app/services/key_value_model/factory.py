from app.core.config import Settings
from app.services.key_value_model.base import KeyValueModel
from app.services.key_value_model.heuristic import HeuristicKeyValueModel


class KeyValueModelFactory:
    @staticmethod
    def create(_: Settings) -> KeyValueModel:
        return HeuristicKeyValueModel()

