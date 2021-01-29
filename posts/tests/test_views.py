import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.forms import fields
from django.test import Client, TestCase
from django.urls import reverse

from posts.constants import POSTS_PER_PAGE
from posts.models import Group, Post


class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_1 = Group.objects.create(
            title='Заголовок группы',
            slug='test-slug',
            description='Описание группы'
        )

        cls.group_2 = Group.objects.create(
            title='Заголовок группы 2',
            slug='test-slug-2',
            description='Описание группы 2',
        )

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.user = get_user_model().objects.create(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            text='Текст поста',
            group=PostPagesTests.group_1,
            author=self.user,
            image=PostPagesTests.uploaded,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={
                              'slug': PostPagesTests.group_1.slug
                          }),
            'new_post.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
        и новый пост отображается на странице.
        """
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(
            response.context.get('page').object_list[0],
            self.post
        )

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом
        и пост добавленный для этой группы отображается на странице.
        """
        response = self.guest_client.get(
            reverse('group', kwargs={'slug': PostPagesTests.group_1.slug})
        )
        group_title = response.context.get('group').title
        group_desc = response.context.get('group').description
        self.assertEqual(group_title, PostPagesTests.group_1.title)
        self.assertEqual(group_desc, PostPagesTests.group_1.description)
        self.assertEqual(
            response.context.get('page').object_list[0],
            self.post
        )

    def test_group_2_page_is_false_post(self):
        """Добавленные пост не должен попасть в группу,
        для которой не был предназначен.
        """
        response = self.guest_client.get(
            reverse('group', kwargs={'slug': PostPagesTests.group_2.slug})
        )
        self.assertEqual(len(response.context.get('page').object_list), 0)

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': fields.ChoiceField,
            'text': fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit', args=[
                self.user.username,
                self.post.id,
            ])
        )
        form_fields = {
            'group': fields.ChoiceField,
            'text': fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('post'), self.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон профайла пользователя сформирован с правильным контекстом
        и пост данного пользователя отображается на странице.
        """
        response = self.guest_client.get(
            reverse('profile', args=[self.user.username])
        )
        self.assertEqual(response.context.get('user_profile'), self.user)
        self.assertEqual(
            response.context.get('page').object_list[0],
            self.post
        )
        self.assertTrue(response.context.get('paginator'))

    def test_post_page_show_correct_context(self):
        """Шаблон страницы отдельного поста сформирован с
        правильным контекстом.
        """
        response = self.guest_client.get(reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': self.post.id}
        ))
        count_user_post = Post.objects.filter(author=self.user).count()
        self.assertEqual(response.context.get('user_profile'), self.user)
        self.assertEqual(
            response.context.get('user_post_count'), count_user_post
        )
        self.assertEqual(response.context.get('post'), self.post)
        self.assertTrue(response.context.get('post_viewing'))


class PaginatorPostTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

        self.user = get_user_model().objects.create(username='StasBasov')

        self.group = Group.objects.create(
            title='Заголовок группы',
            slug='test-slug',
            description='Описание группы'
        )

        objs = (Post(
            text='Текст поста',
            group=self.group,
            author=self.user,
        ) for i in range(13))
        Post.objects.bulk_create(objs)

        self.paginator_page_name = {
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
        }

    def test_first_page_containse_ten_records(self):
        """Paginator выводит правильное количество публикаций на первой стр."""
        for reverse_name in self.paginator_page_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    POSTS_PER_PAGE
                )

    def test_second_page_containse_three_records(self):
        """Paginator выводит правильное количество публикаций на второй стр."""
        for reverse_name in self.paginator_page_name:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    3
                )
