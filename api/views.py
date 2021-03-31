import uuid

from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import EMAIL_ADDRESS, EMAIL_SUBJECT

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import (IsAdmin, IsAdminOrReadOnly, IsAuthor, IsModerator,
                          IsSuperuser)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleCreateSerializer, TitleListSerializer,
                          UserSerializer)

CUSTOM_PERMISSIONS = (
    IsAuthenticatedOrReadOnly,
    IsAuthor | IsModerator | IsAdminOrReadOnly | IsSuperuser
)


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        email = request.data.get('email')
        if email is None:
            return Response(
                {'email': 'Incorrect or None'},
                status=HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=email).first()
        if user is None:
            confirmation_code = str(uuid.uuid4())
            data = {
                'email': email,
                'confirmation_code': confirmation_code,
                'username': email
            }
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            confirmation_code = user[0].confirmation_code
        user.send_mail(subject=EMAIL_SUBJECT, message=confirmation_code,
                       from_email=EMAIL_ADDRESS)
        return Response({'email': email})


class TokenView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def get_token(user):
        return str(RefreshToken.for_user(user).access_token)

    def post(self, request):
        user = get_object_or_404(User, email=request.data.get('email'))
        if user.confirmation_code != request.data.get('confirmation_code'):
            return Response(
                {'confirmation_code': 'Incorrect code for this email'},
                status=HTTP_400_BAD_REQUEST
            )
        return Response({'token': self.get_token(user)}, status=HTTP_200_OK)


class UsersViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsSuperuser | IsAdmin)
    lookup_field = 'username'

    @action(detail=False, permission_classes=(IsAuthenticated,),
            methods=('get', 'patch'), url_path='me')
    def get_or_update_self(self, request):
        if request.method == 'GET':
            return Response(self.get_serializer(request.user, many=False).data)
        else:
            if (
                request.user.role != 'admin'
                and request.data.get('role') is not None
            ):
                return Response(
                    {'role': 'Only Admin can change roles users'},
                    status=HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class TitlesViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    filter_backends = (DjangoFilterBackend, SearchFilter)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        return (
            TitleCreateSerializer if self.action
            in ('create', 'update', 'partial_update') else TitleListSerializer
        )


class CreateListDestroyViewSet(ListModelMixin, CreateModelMixin,
                               DestroyModelMixin, GenericViewSet):
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = CUSTOM_PERMISSIONS

    def get_queryset(self):
        return get_object_or_404(
            Review.objects.filter(title_id=self.kwargs.get('title_id')),
            pk=self.kwargs.get('review_id')
        ).comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review.objects.filter(title_id=self.kwargs.get('title_id')),
                pk=self.kwargs.get('review_id'))
        )


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = CUSTOM_PERMISSIONS
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        ).reviews.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        )
