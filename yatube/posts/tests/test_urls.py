from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages(self):
        """Test pages: index, about_author, tech"""
        url_names = [
            '/',
            '/about/author/',
            '/about/tech/',
        ]
        for address in url_names:
            with self.subTest(template=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.slug = 'test_slug'
        cls.username = 'HasNoName'

        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=cls.slug,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        Post.objects.all().delete()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_non_existent_page_correct_status_code(self):
        response = self.client.get('/non_existent_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_non_auth_urls_correct_status_code(self):
        url_names_non_auth = ['/',
                              f'/group/{self.slug}/',
                              f'/profile/{self.username}/',
                              f'/posts/{self.post.id}/']
        for address in url_names_non_auth:
            with self.subTest(adress=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_post_edit_url_correct_status_code(self):
        url = f'/posts/{self.post.id}/edit/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_create_url_correct_status_code(self):
        url = '/create/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        url_templates_names_all = {
            '/': 'posts/index.html',
            f'/group/{self.slug}/': 'posts/group_list.html',
            f'/profile/{self.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/non_existent_page/': 'core/404.html',
        }
        for address, template in url_templates_names_all.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
