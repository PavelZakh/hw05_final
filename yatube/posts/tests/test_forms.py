import tempfile
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'Name'
        cls.new_post_text = 'New post'
        cls.edited_post_text = 'Edited post'
        cls.image_name = 'small'
        cls.regexp = rf'.*{cls.image_name}.*\.png'

        small_png = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name=f'{cls.image_name}.png',
            content=small_png,
            content_type='image/gif')

        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug0',
            description='test description0',
        )
        cls.another_group = Group.objects.create(
            title='Another title',
            slug='test_slug1',
            description='test description1',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Test comment',
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Correct post creation test"""
        post_count = Post.objects.count()
        form_data = {
            'text': self.new_post_text,
            'group': self.group.id,
            'image': self.image,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.username})
        )

        self.assertEqual(Post.objects.count(), post_count + 1)

        posts_order_pk = Post.objects.order_by("pk")
        last_post = posts_order_pk.reverse()[0]
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertRegex(str(last_post.image), self.regexp)

    def test_edit_post(self):
        """Correct post edit"""
        form_data = {
            'text': self.edited_post_text,
            'group': self.another_group.id,
        }

        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )

        post = Post.objects.get(pk=self.post.id)
        post_text = post.text
        post_group = post.group

        self.assertRedirects(
            response_edit,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

        self.assertEqual(post_text, form_data['text'])
        self.assertEqual(post_group.id, form_data['group'])

    def test_guest_create_post(self):
        form_data = {
            'text': self.new_post_text,
            'group': self.group.id,
        }
        before_create_posts_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.request['PATH_INFO'], reverse('users:login'))
        self.assertEqual(before_create_posts_count, Post.objects.count())

    def test_guest_edit_post(self):
        form_data = {
            'text': self.edited_post_text,
            'group': self.another_group.id,
        }
        post_before = Post.objects.get(pk=self.post.id)
        response_edit = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        post_after = Post.objects.get(pk=self.post.id)
        self.assertEqual(
            response_edit.request['PATH_INFO'],
            reverse('users:login')
        )
        self.assertEqual(
            post_before.text,
            post_after.text
        )
        self.assertEqual(
            post_before.group,
            post_after.group
        )

    def test_comment_auth_user(self):
        post = Post.objects.get(pk=self.post.id)
        comments_count = post.comments.count()
        form_data = {
            'text': 'Test comment'
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.request['PATH_INFO'], reverse('users:login'))
        self.assertEqual(comments_count, post.comments.count())

    def test_create_comment(self):
        """Correct comment creation test"""
        comments_before_count = self.post.comments.count()
        form_data = {
            'text': 'Test comment23'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

        comments_after_count = self.post.comments.count()
        self.assertEqual(comments_after_count, comments_before_count + 1)

        posts_order_pk = self.post.comments.order_by("pk")
        last_comment = posts_order_pk.reverse()[0]
        self.assertEqual(last_comment.text, form_data['text'])
        self.assertEqual(last_comment.post.id, self.post.id)
        self.assertEqual(last_comment.author, self.user)
