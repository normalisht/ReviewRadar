from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Title, Genre, Category, Review
from .filters import TitleFilter
from .mixins import CreateListDestroyMixin
from .permissions import (IsAuthor, IsAdmin, IsModerator, ReadOnly,
                          IsSuperuser, IsYourself)
from .serializers import (TitleReadSerializer, TitleWriteSerializer,
                          GenreSerializer, CategorySerializer,
                          CommentSerializer, ReviewSerializer, User,
                          UserSerializer, SignupSerializer, TokenSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')
                                      ).all().order_by('id')
    permission_classes = [IsAdmin | ReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class GenreViewSet(CreateListDestroyMixin):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer


class CategoryViewSet(CreateListDestroyMixin):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdmin | IsModerator | IsAuthor | ReadOnly]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        review_id = self.kwargs['review_id']

        title = get_object_or_404(
            Title.objects.prefetch_related('reviews', 'reviews__comments'),
            id=title_id
        )

        return title.reviews.get(id=review_id).comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs['review_id']
        review = get_object_or_404(title.reviews, id=review_id)

        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdmin | IsModerator | IsAuthor | ReadOnly]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        return Review.objects.filter(title__id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

    def get_serializer_context(self):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, id=title_id)

        context = super().get_serializer_context()
        context.update({"title": title, 'author': self.request.user})
        return context


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperuser | IsAdmin | IsYourself]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    lookup_field = 'username'
    search_fields = ('username',)
    ordering = ('username',)

    def get_object(self):
        if self.kwargs.get('username') == 'me':
            return self.request.user
        return super().get_object()

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.kwargs.get('username') != 'me' and request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def me_patch(self, request):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @me.mapping.delete
    def me_delete(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SignupView(APIView):
    serializer_class = SignupSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, created = User.objects.get_or_create(
            email=serializer.validated_data.get('email'),
            username=serializer.validated_data.get('username')
        )

        user.confirmation_code = default_token_generator.make_token(user)
        user.save(update_fields=['confirmation_code'])

        send_mail(
            'Confirmation code',
            f'Confirmation code: {user.confirmation_code}',
            settings.ADMIN_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({
            'email': user.email,
            'username': user.username
        }, status=status.HTTP_200_OK)


class TokenObtainPairView(APIView):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        confirmation_code = serializer.validated_data.get('confirmation_code')

        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': 'Неправильный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            },
            status=status.HTTP_200_OK
        )
