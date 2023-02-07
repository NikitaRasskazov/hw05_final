from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

TITLE_MAX_LENGTH = 200
SLUG_MUX_LENGTH = 50
NUMBER_OF_CHARACTERS = 15
CHARACTERS_IN_COMMENT = 30


class Group(models.Model):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Группа'
    )
    slug = models.SlugField(max_length=SLUG_MUX_LENGTH, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Содержание')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:NUMBER_OF_CHARACTERS]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:CHARACTERS_IN_COMMENT]
