from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer, SlugRelatedField,
                                        ValidationError)

from .models import Category, Comment, Genre, Review, Title, User


class UserSerializer(ModelSerializer):
    """User serialiser."""

    role = CharField(default='user')

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role',
            'confirmation_code'
        )
        model = User
        extra_kwargs = {
            'confirmation_code': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }


class ReviewSerializer(ModelSerializer):
    """Review serialiser."""

    author = SlugRelatedField('username', read_only=True, many=False)

    class Meta:
        read_only_fields = ('id', 'title', 'pub_date')
        fields = '__all__'
        model = Review

    def validate(self, attrs):
        is_exist = Review.objects.filter(
            author=self.context['request'].user,
            title=self.context['view'].kwargs.get('title_id')
        ).exists()
        if is_exist and self.context['request'].method == 'POST':
            raise ValidationError('You have already left your review')
        return attrs


class CommentSerializer(ModelSerializer):
    """Comment serialiser."""

    author = SlugRelatedField('username', read_only=True, many=False)

    class Meta:
        read_only_fields = ('id', 'review', 'pub_date')
        fields = '__all__'
        model = Comment


class CategorySerializer(ModelSerializer):
    """Category serialiser."""

    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenreSerializer(ModelSerializer):
    """Genre serialiser."""

    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitleListSerializer(ModelSerializer):
    """Serialiser for the output of a list of works."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleCreateSerializer(ModelSerializer):
    """Serialiser for the creation of works."""

    category = SlugRelatedField(
        'slug',
        queryset=Category.objects.all()
    )
    genre = SlugRelatedField(
        'slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title
