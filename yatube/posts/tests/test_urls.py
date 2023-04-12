from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post
from .test_views import DESCRIPTION, FIRST_TITLE, SLUG, TEXT_ONE, USER_ONE

User = get_user_model()
unexisting_page = '/unexisting_page/'


# python3 manage.py test posts.tests.test_urls для запуска локальных тестов

class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_ONE)
        cls.group = Group.objects.create(
            title=FIRST_TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT_ONE,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{SLUG}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            f'{unexisting_page}': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /unexisting_page/."""
        response = self.client.get(unexisting_page)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_all_page_for_any_client_at_desired_location(self):
        """Страницы доступные всем пользователям."""
        url = {
            "/",
            f"/group/{SLUG}/",
            f"/profile/{self.user}/",
            f"/posts/{self.post.pk}/",
        }
        for address in url:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_and_create_url_exists_at_desired_location(self):
        """
            Страницы posts/<int:post_id>/edit/, create/ доступны
            авторизованному пользователю.
        """
        url = {
            f'/posts/{self.post.pk}/edit/',
            '/create/',
        }
        for address in url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_client_can_follow(self):
        """
            Страница '/follow/',
            доступна авторизованному пользователю.
        """
        url = '/follow/'
        response = self.authorized_client.get(url)
        second_response = self.client.get(url)
        # Проверяем, что авторизованному пользователю доступна страница
        # с подписками
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/follow.html')
        # Проверяем, что не авторизованному пользователю при запросе
        # страницы с подписками происходит редирект
        self.assertEqual(second_response.status_code, HTTPStatus.FOUND)

