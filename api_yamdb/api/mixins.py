from rest_framework import mixins, viewsets, filters

from .permissions import IsAdmin, ReadOnly


class CreateListDestroyMixin(mixins.CreateModelMixin, mixins.ListModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    """Миксин на создание, удаление и получение списка объектов.
    С доступом к объекту по полю 'slug'.
    С фильтрацией по полям 'name' и 'slug'.
    С уровнем доступа 'Админ или только чтение'."""

    permission_classes = [IsAdmin | ReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('slug', 'name')
    lookup_field = 'slug'
