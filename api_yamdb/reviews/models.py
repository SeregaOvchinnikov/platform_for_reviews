from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

from reviews.validators import validate_username


class Genre(models.Model):
    """Жанр произведения"""

    name = models.CharField(
        max_length=256,
        verbose_name="Жанр произведения",
        help_text="Жанр произведения"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Slug для URL",
        help_text="Короткое имя для URL",
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return self.slug


class Category(models.Model):
    """Категории произведений"""

    name = models.CharField(
        max_length=256,
        verbose_name="Категория произведения",
        help_text="Категория произведения",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Slug для URL",
        help_text="Короткое имя для URL",
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория произведения'
        verbose_name_plural = 'Категории произведений'


class User(AbstractUser):
    USER = "user"
    MODER = "moderator"
    ADMIN = "admin"
    ROLES = [
        (USER, "Аутентифицированный пользователь"),
        (MODER, "Модератор"),
        (ADMIN, "Администратор"),
    ]

    username = models.CharField(
        max_length=150, unique=True, validators=[validate_username]
    )
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    email = models.EmailField("Почта", unique=True, max_length=254)
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    role = models.CharField(
        "Роль",
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=USER,
    )
    confirmation_code = models.CharField(
        max_length=150, blank=True, verbose_name="Код для идентификации"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = (
            models.UniqueConstraint(
                fields=("username", "email"), name="unique_together",
            ),
        )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODER

    def __str__(self):
        return self.username[:20]


class Title(models.Model):
    """Произведение"""

    name = models.CharField(
        max_length=256,
        verbose_name="Название произведения",
        help_text="Название произведения",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="добавьте описание"
    )
    year = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(timezone.now().year)],
        verbose_name='Год выпуска',
        help_text='укажите год выпуска'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр произведения",
        help_text="укажите жанр произведения",
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория произведения',
        help_text='укажите категорию произведения',
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Отзывы к произведениям"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
        help_text="Автор отзыва",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Произведение",
        help_text="Название произведения",
    )
    text = models.TextField(
        verbose_name="Текст отзыва",
        help_text="Текст отзыва",
    )
    score = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10),
        ),
        verbose_name="Рейтинг произведения",
        help_text="Рейтинг произведения",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        help_text="Дата публикации",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=(
                    "title",
                    "author",
                ),
                name="unique_title_author",
            ),
        )
        ordering = ("-pub_date",)
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Комментарии к отзывам"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
        help_text="Автор комментария",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
        help_text="Отзыв",
    )
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Текст комментария",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
        help_text="Дата публикации",
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:15]
