import tempfile
import shutil

from django.conf import settings
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..models import Group, Post, Follow
from yatube.settings import PAGE_POSTS_COUNT

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_on_page = PAGE_POSTS_COUNT
        cls.slug = 'test_slug'
        cls.wrong_slug = 'wrong_slug'
        cls.username = 'HasNoName'
        cls.flwr_usrnm = 'Follower'
        cls.post_id = '1'
        cls.posts_count = 12

        cls.user_follower = User.objects.create_user(username=cls.flwr_usrnm)
        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title='Test group',
            slug=cls.slug,
            description='Test description',
        )
        cls.group_wrong = Group.objects.create(
            title='Wrong group',
            slug=cls.wrong_slug,
            description='Wrong description',
        )
        small_png = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.png',
            content=small_png,
            content_type='image/gif')
        objects = (Post(
            pk=i,
            author=cls.user,
            text='Test post %s' % i,
            group=cls.group,
            image=uploaded
        ) for i in range(cls.posts_count))
        cls.posts_bulk = Post.objects.bulk_create(
            objects,
            cls.posts_count
        )

    @classmethod
    def tearDownClass(cls):
        Post.objects.all().delete()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.auth_follower_client = Client()
        self.auth_follower_client.force_login(self.user_follower)

    def test_pages_correct_template(self):
        """All URLs uses the appropriate template."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_page', kwargs={'slug': self.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.username}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post_id}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}): (
                'posts/create_post.html'
            ),
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_correct_context(self):
        """index, group_page and profile page get correct context."""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_page', kwargs={'slug': self.slug}),
            reverse('posts:profile', kwargs={'username': self.username}),
        ]
        for template in pages_names:
            with self.subTest(template=template):
                response = self.client.get(template)

                post = response.context['page_obj'].paginator.object_list[0]

                self.assertEqual(
                    post.id,
                    self.posts_bulk[-1].pk
                )
                self.assertEqual(
                    post.text,
                    self.posts_bulk[-1].text
                )
                self.assertEqual(
                    post.image,
                    self.posts_bulk[-1].image
                )
                self.assertEqual(post.author, self.user)
                self.assertEqual(post.group, self.group)

    def test_urls_first_page_contains_required_posts_quantity(self):
        """index, group_page, profile. First page required posts displayed"""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_page', kwargs={'slug': self.slug}),
            reverse('posts:profile', kwargs={'username': self.username}),
        ]

        for template in pages_names:
            with self.subTest(template=template):
                response = self.client.get(template)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.posts_on_page
                )

    def test_urls_second_page_required_posts_quantity(self):
        """index, group_page, profile. Second page required posts displayed"""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_page', kwargs={'slug': self.slug}),
            reverse('posts:profile', kwargs={'username': self.username}),
        ]

        for template in pages_names:
            with self.subTest(template=template):
                response = self.client.get(template + '?page=2')

                second_page_posts = Post.objects.count() - self.posts_on_page
                if second_page_posts >= self.posts_on_page:
                    posts_remain = self.posts_on_page
                else:
                    posts_remain = second_page_posts

                self.assertEqual(
                    len(response.context['page_obj']),
                    posts_remain
                )

    def test_profile_correct_context(self):
        """post_detail page correct context."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_id})
        )
        post = response.context['post']
        self.assertEqual(
            post.text,
            Post.objects.get(pk=self.post_id).text
        )
        self.assertEqual(
            post.image,
            self.posts_bulk[int(self.post_id)].image
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)

    def test_post_create_and_edit_correct_context(self):
        """post create and edit correct form context."""
        pages_names = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for template in pages_names:
            response = self.authorized_client.get(template)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_create_correct(self):
        """post is displayed correctly on the pages index, group, profile."""
        post = Post.objects.create(
            author=self.user,
            text='Post about nature',
            group=self.group
        )

        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_page', kwargs={'slug': self.slug}),
            reverse('posts:profile', kwargs={'username': self.username}),
        ]

        for template in pages_names:
            with self.subTest(template=template):
                response = self.client.get(template)
                last_page_post = response.context['page_obj'][0]
                self.assertEqual(last_page_post, post)

        self.assertNotIn(post, self.group_wrong.posts.all())

    def test_follow_author(self):
        response_follow = self.auth_follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.username})
        )
        self.assertRedirects(
            response_follow,
            reverse('posts:profile', kwargs={'username': self.username})
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user_follower,
            author=self.user,
        ).exists())

    def test_unfollow_author(self):
        response_unfollow = self.auth_follower_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.username})
        )
        self.assertRedirects(
            response_unfollow,
            reverse('posts:profile', kwargs={'username': self.username})
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower,
            author=self.user,
        ).exists())

    def test_follow_posts_correct_displayed(self):
        Follow.objects.create(
            user=self.user_follower,
            author=self.user,
        )
        response_follower = self.auth_follower_client.get(
            reverse('posts:follow_index'))
        self.assertTrue(response_follower.context['page_obj'])

        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertFalse(response.context['page_obj'])
