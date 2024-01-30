from django_filters.rest_framework import FilterSet, CharFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    genre = CharFilter(field_name='genre__slug', lookup_expr='contains')
    category = CharFilter(field_name='category__slug', lookup_expr='contains')

    class Meta:
        model = Title
        fields = ('genre', 'year', 'name', 'category')
