import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, EmailField,
                              ForeignKey, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField,
                              TextChoices, TextField)
from django.db.models.deletion import DO_NOTHING

from .validators import validator_pub_year

SCORE_VALIDATORS = (
    MinValueValidator(1),
    MaxValueValidator(10)
)


class User(AbstractUser):
    """User augmented fields."""

    class RoleUser(TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    bio = TextField(
        verbose_name='bio',
        max_length=1000,
        blank=True
    )
    role = CharField(
        verbose_name='role',
        max_length=50,
        blank=True,
        choices=RoleUser.choices,
        default=RoleUser.USER
    )
    email = EmailField(
        verbose_name='email',
        max_length=255,
        unique=True
    )
    confirmation_code = CharField(
        verbose_name='confirmation code',
        max_length=100,
        null=True,
        default=str(uuid.uuid4())
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @property
    def is_admin(self):
        return self.is_staff or self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class Category(Model):
    """Types of works (Movies, Books, Music)."""

    name = CharField(
        verbose_name='category',
        max_length=100,
        blank=True,
        null=True
    )
    slug = SlugField(
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Genre(Model):
    """Genres of works

    One work can be linked to more than one genre.
    """

    name = CharField(
        verbose_name='genre',
        max_length=100,
        blank=True,
        null=True
    )
    slug = SlugField(
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = 'genre'
        verbose_name_plural = 'genres'

    def __str__(self):
        return self.name


class Title(Model):
    """Works for which reviews are written."""

    name = CharField(
        verbose_name='title',
        max_length=200,
        blank=True,
        null=True
    )
    genre = ManyToManyField(
        Genre,
        related_name='title'
    )
    category = ForeignKey(
        Category,
        related_name='title',
        null=True,
        on_delete=DO_NOTHING
    )
    description = TextField(
        verbose_name='description',
        blank=True,
        null=True
    )
    year = PositiveSmallIntegerField(
        verbose_name='year',
        validators=[validator_pub_year],
        null=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'title'
        verbose_name_plural = 'titles'

    def __str__(self):
        return self.name


class Review(Model):
    """Reviews of works

    Review is linked to a specific piece of work.
    """

    text = TextField(
        verbose_name='review',
        max_length=2000
    )
    author = ForeignKey(
        User,
        verbose_name='author',
        on_delete=CASCADE,
        related_name='reviews'
    )
    title = ForeignKey(
        Title,
        verbose_name='title',
        on_delete=CASCADE,
        related_name='reviews'
    )
    pub_date = DateTimeField(
        verbose_name='pub date',
        auto_now_add=True
    )
    score = PositiveSmallIntegerField(
        verbose_name='score',
        default=0,
        validators=SCORE_VALIDATORS,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'review'
        verbose_name_plural = 'reviews'

    def __str__(self):
        return self.title


class Comment(Model):
    """Comments on the feedback

    Comment is linked to a specific review.
    """

    text = TextField(
        verbose_name='comment',
        max_length=2000
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='author'
    )
    review = ForeignKey(
        Review,
        on_delete=CASCADE,
        related_name='comments',
        verbose_name='review'
    )
    pub_date = DateTimeField(
        verbose_name='pub date',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return self.text
