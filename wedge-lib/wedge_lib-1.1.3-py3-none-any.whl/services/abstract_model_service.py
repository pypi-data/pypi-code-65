from django.db import models

from w.services.abstract_service import AbstractService
from w import exceptions


# noinspection PyCallingNonCallable
class AbstractModelService(AbstractService):
    _model: models.Model

    @classmethod
    def is_exists_by_id(cls, model_id) -> bool:
        """
        Check model exists
        """
        qs = cls._model.objects.filter(pk=model_id)
        return qs.exists()

    @classmethod
    def check_by_id(cls, model_id) -> models.Model:
        """
        Check model exists by id, if not raise NotFoundError else return model
        """
        try:
            return cls._model.objects.get(pk=model_id)
        except cls._model.DoesNotExist:
            label = cls._model._meta.verbose_name.title()
            raise exceptions.NotFoundError(f"{label} not found (id={model_id})")

    @classmethod
    def create(cls, **attrs) -> models.Model:
        """
        Create model instance

        Args:
            **attrs: model attributes values

        Returns:
            models.Model
        """
        model = cls._model(**attrs)
        model.save()
        return model
