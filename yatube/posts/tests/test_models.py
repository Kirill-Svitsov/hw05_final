from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import NUM_OF_WORDS, Group, Post
from .test_views import DESCRIPTION, FIRST_TITLE, SLUG, TEXT_ONE, USER_ONE

User = get_user_model()


# python3 manage.py test posts.tests.test_models для запуска локальных тестов
class PostModelTest(TestCase):
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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        fields_post_group = {
            self.post.text[:NUM_OF_WORDS]: str(self.post),
            self.group.title: str(self.group)
        }
        for key, value in fields_post_group.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Заглавие',
            'slug': 'Уникальный URL',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)
