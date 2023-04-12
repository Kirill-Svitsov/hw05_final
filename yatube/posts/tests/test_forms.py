import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User
from .test_views import (DESCRIPTION, FIRST_TITLE, SLUG, TEXT_ONE, USER_ONE,
                         USER_TWO)

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# python3 manage.py test posts.tests.test_forms для запуска локальных тестов

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_ONE)
        cls.user_two = User.objects.create_user(username=USER_TWO)
        cls.group = Group.objects.create(
            title=FIRST_TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT_ONE,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись"""
        # считаем количество записей в БД
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        # Заполняем форму для записи в БД
        form_data = {'text': 'Текст поста',
                     'group': self.group.id,
                     'image': uploaded
                     }
        # Отправляем запись в БД
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        # Проверяем редирект на страницу пользователя после отправки формы
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': USER_ONE})
                             )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         )
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])

    def test_guest_client_create_post(self):
        """Создание записи возможно только авторизованному пользователю"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.pk,
        }
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_authorized_edit_post(self):
        """Редактирование записи автором поста"""
        # Считаем количество постов в базе
        post_count = Post.objects.count()
        # Заполняем форму
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.pk}
        # Отправляем форму
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True)
        # Проверяем, что новая запись не создалась
        self.assertEqual(Post.objects.count(), post_count)
        # Проверяем редирект на страницу post_detail после редактирования
        self.assertRedirects(response,
                             reverse('posts:post_detail', args=(self.post.pk,))
                             )
        # Получаем для проверки объект поста из БД
        post = Post.objects.get(pk=self.post.pk)
        # Проверяем автора
        self.assertEqual(post.author, self.post.author)
        # Проверяем изменился ли текст записи
        self.assertEqual(post.text, form_data['text'])
        # Проверяем сохранилась ли группа записи
        self.assertEqual(post.group.pk, form_data['group'])

    def test_guest_client_create_comment(self):
        """Создание комментария невозможно неавторизованному пользователю"""
        post = Post.objects.get(pk=self.post.pk)
        comments_count = post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=False
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(post.comments.count(), comments_count)

    def test_auth_client_create_comment(self):
        """Авторизованный пользователь может оставить комментарий"""
        post = Post.objects.get(pk=self.post.pk)
        comments_count = post.comments.count()
        # Заполняем форму для комментария
        form_data = {'text': 'Текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=False
        )
        # Проверяем редирект после отправки комментария
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk})
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(
            post.comments.count(),
            comments_count + 1,
        )

