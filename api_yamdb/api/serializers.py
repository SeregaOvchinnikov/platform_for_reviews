import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.errors import ErrorMesage
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):
    category = CategoryField(
        slug_field="slug", queryset=Category.objects.all(), required=False
    )
    genre = GenreField(slug_field="slug", queryset=Genre.objects.all(),
                       many=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = "__all__"

    def validate_year(self, value):
        year = datetime.date.today().year
        if year < value:
            raise serializers.ValidationError(ErrorMesage.INVALID_YEAR)
        return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(validate_username,
                    UniqueValidator(queryset=User.objects.all()),),
    )

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name", "bio", "role"
        )
        validators = (
            UniqueTogetherValidator(
                queryset=User.objects.all(), fields=("username", "email")
            ),
        )


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True, max_length=150, validators=[validate_username]
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True, max_length=150, validators=(validate_username,)
    )
    confirmation_code = serializers.CharField(required=True, max_length=150)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Review
        exclude = ("title",)
        read_only_fields = ("pub_date",)

    def validate(self, data):
        if self.context["request"].method != "POST":
            return data

        title_id = self.context["view"].kwargs.get("title_id")
        author = self.context["request"].user

        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(ErrorMesage.ONLY_ONE_REVIEW)

        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Comment
        exclude = ("review",)
        read_only_fields = ("review", "pub_date")
