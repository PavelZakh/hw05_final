import time

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PagesCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'Name'
        cls.cache_sec = 21

        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post',
            group=cls.group
        )

    def test_cash_index_page(self):
        response_index = self.client.get(reverse('posts:index'))
        Post.objects.filter(pk=self.post.id).delete()
        self.assertContains(response_index, self.post.text)
        time.sleep(self.cache_sec)
        response = self.client.get(reverse('posts:index'))
        self.assertNotContains(response, self.post.text)
