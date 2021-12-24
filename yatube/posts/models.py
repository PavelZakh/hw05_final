from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
        null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        # выводим текст поста
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'


class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите текст комментария',
        null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )


class Follow(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
