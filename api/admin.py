from django.contrib.admin import ModelAdmin, register

from .models import Category, Comment, Genre, Review, Title, User


@register(Category)
class CategoryAdmin(ModelAdmin):
    """Category administration."""

    list_display = ('id', 'name', 'slug')
    empty_value_display = '-пусто-'


@register(Genre)
class GenreAdmin(ModelAdmin):
    """"Genre administration."""

    list_display = ('id', 'name', 'slug')
    empty_value_display = '-пусто-'


@register(Title)
class TitleAdmin(ModelAdmin):
    """Title administration."""

    list_display = ('id', 'name', 'year', 'description', 'category')
    empty_value_display = '-пусто-'


@register(Review)
class ReviewAdmin(ModelAdmin):
    """Review administration."""

    list_display = ('id', 'text', 'author', 'score', 'pub_date')
    empty_value_display = '-пусто-'


@register(Comment)
class CommentAdmin(ModelAdmin):
    """Comment administration."""

    list_display = ('id', 'text', 'author', 'pub_date')
    empty_value_display = '-пусто-'


@register(User)
class UserAdmin(ModelAdmin):
    """User administration."""

    list_display = ('email', 'username', 'role')
    empty_value_display = '-пусто-'
