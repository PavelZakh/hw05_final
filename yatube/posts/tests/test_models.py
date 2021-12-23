from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    @classmethod
    def tearDownClass(cls):
        Post.objects.all().delete()

    def test_models_have_correct_object_names(self):
        """Check that the __str__ works correctly for the models ."""
        group = PostModelTest.group
        post = PostModelTest.post

        expected_group_str = group.title
        expected_post_str = post.text[:15]

        self.assertEqual(expected_group_str, str(group))
        self.assertEqual(expected_post_str, str(post))
