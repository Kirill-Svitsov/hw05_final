import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post
from ..views import num_of_pub

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEXT_ONE = 'Текст поста один'
TEXT_TWO = 'Текст поста два'
FIRST_TITLE = 'Тестовая группа'
SECOND_TITLE = 'Вторая группа'
SLUG = 'test_slug'
SECOND_SLUG = 'test_slug_second'
DESCRIPTION = 'Тестовое описание'
SECOND_DESCRIPTION = 'Тестовое описание 2'
USER_ONE = 'HasNoName'
USER_TWO = 'Second_User'
POSTS_OF_FIRST_AUTHOR = 13
POSTS_OF_SECOND_AUTHOR = 2
POSTS_PAGINATOR_SECOND_PAGE = 5
POSTS_OF_GROUP_PAGE = 2


# python3 manage.py test posts.tests.test_views для запуска локальных тестов
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_ONE)
        cls.second_user = User.objects.create_user(username=USER_TWO)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=FIRST_TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.second_group = Group.objects.create(
            title=SECOND_TITLE,
            slug=SECOND_SLUG,
            description=SECOND_DESCRIPTION
        )
        for post in range(POSTS_OF_FIRST_AUTHOR):
            cls.post = Post.objects.create(
                text=TEXT_ONE,
                author=cls.user,
                group=cls.group,
                image=cls.image
            )
        for post in range(POSTS_OF_SECOND_AUTHOR):
            cls.post = Post.objects.create(
                text=TEXT_TWO,
                author=cls.second_user,
                group=cls.second_group,
                image=cls.image
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.second_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile',
                    kwargs={'username': USER_TWO}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:group_list',
                    kwargs={'slug': SLUG}): 'posts/group_list.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        post_group_list = list(Post.objects.filter(
            group_id=self.group.id
        )[:10])
        self.assertEqual(list(response.context['page_obj']), post_group_list)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': USER_TWO}))
        first_post = response.context['page_obj'][0]
        post_author_0 = first_post.author
        self.assertEqual(post_author_0, PostViewsTests.post.author)
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_OF_SECOND_AUTHOR
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_post = response.context['post']
        self.assertEqual(first_post.pk, PostViewsTests.post.pk)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.post.pk,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_paginator_first_page_contains_ten_records(self):
        """Первая страница содержит 10 записей."""
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), num_of_pub)

    def test_paginator_second_page_contains_five_records(self):
        """Вторая страница содержит 5 записей."""
        cache.clear()
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_PAGINATOR_SECOND_PAGE
        )

    def test_paginator_group_list_contains_two_records(self):
        """Страница группы содержит 2 записи."""
        cache.clear()
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': SECOND_SLUG})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_OF_GROUP_PAGE
        )

    def test_paginator_profile_contains_two_records(self):
        """Страница профиля содержит 2 записи."""
        cache.clear()
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': USER_TWO})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            POSTS_OF_SECOND_AUTHOR
        )

    def test_index_page_cache(self):
        """Тест cache на странице index."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text=TEXT_TWO,
            author=self.user,
        )
        response_cache_one = self.authorized_client.get(reverse('posts:index'))
        posts_with_cache = response_cache_one.content
        self.assertEqual(posts_with_cache, posts)
        cache.clear()
        response_without_cache = self.authorized_client.get(
            reverse('posts:index')
        )
        new_posts = response_without_cache.content
        self.assertNotEqual(posts_with_cache, new_posts)


class FollowTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.client_auth_user = Client()
        self.client_auth_author = Client()
        self.user = User.objects.create_user(username=USER_ONE)
        self.author = User.objects.create_user(username=USER_TWO)
        self.post = Post.objects.create(
            author=self.author,
            text=TEXT_ONE
        )
        self.client_auth_user.force_login(self.user)
        self.client_auth_author.force_login(self.author)

    def _subscribe(self, subscribe: bool, author: str) -> None:
        """
        Метод позволяет подписаться на автора или отписаться
        """
        if subscribe:
            self.client_auth_user.get(
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': author}
                )
            )
        else:
            self.client_auth_user.get(
                reverse(
                    'posts:profile_unfollow',
                    kwargs={'username': author}
                )
            )

    def test_ability_subscribe(self):
        """
        Авторизованный пользователь может подписываться на других пользователей
        """
        self._subscribe(True, self.author)
        self.assertEqual(
            Follow.objects.filter(user=self.user, author=self.author).count(),
            1
        )

    def test_ability_unsubscribe(self):
        """
        Авторизованный пользователь может отписаться от других пользователей
        """
        self._subscribe(True, self.author)
        self._subscribe(False, self.author)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_post_in_news_subscriber(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан
        """
        self._subscribe(True, self.author)
        response_subscribe = self.client_auth_user.get(
            reverse('posts:follow_index')
        )
        response_unsubscribe = self.client_auth_author.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            response_subscribe.context['page_obj'][0],
            Post.objects.first()
        )
        self.assertEqual(
            len(response_unsubscribe.context['page_obj']),
            0
        )

    def test_no_follow_to_myself(self):
        """Юзер не может подписаться сам на себя"""
        self._subscribe(True, self.user)
        self.assertEqual(self.user.follower.count(), 0)

    def test_follow_only_one(self):
        """Юзер может подписаться только один раз"""
        self._subscribe(True, self.author)
        self._subscribe(True, self.author)
        self.assertEqual(self.user.follower.count(), 1)
