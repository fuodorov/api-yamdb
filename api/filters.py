from django_filters import CharFilter, FilterSet

from .models import Title


class TitleFilter(FilterSet):
    """Filter works by name, category, genre, year."""

    name = CharFilter(
        field_name='name',
        lookup_expr='contains'
    )
    category = CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    genre = CharFilter(
        field_name='genre__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Title
        fields = ('name', 'category', 'genre', 'year')
