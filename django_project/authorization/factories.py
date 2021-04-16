import factory
from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    login = factory.Sequence(lambda n: 'login_{}'.format(n))
    password = 'password'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)

    class Meta:
        model = User