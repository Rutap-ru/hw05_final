from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = get_user_model().objects.create(username='AndreyG')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

        self.user2 = get_user_model().objects.create(username='Semen')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)

        self.post = Post.objects.create(
            text='Текст поста',
            group=PostURLTests.group,
            author=self.user,
        )

        self.page_url_names_guest = {
            'index.html': reverse('index'),
            'group.html': reverse(
                              'group',
                              kwargs={'slug': PostURLTests.group.slug}
                          ),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
            'profile.html': reverse(
                                'profile',
                                kwargs={'username': self.user.username}
                            ),
            'post.html': reverse('post', kwargs={
                             'username': self.user.username,
                             'post_id': self.post.id,
                         }),
        }

    def test_new_post_url_exists_at_desired_location(self):
        """Страница по адресу /new/ доступна для
        авторизированного пользователя.
        """
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('new_post'))

    def test_post_edit_url_author_access(self):
        """Страница редактирования поста, доступна для автора."""
        response = self.authorized_client_author.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            }),
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_redirect_users_on_post_page(self):
        """Стр. редактирования поста, любого пользователя
        кроме автора перенаправит на стр. поста.
        """
        user_redirect_post_edit = {
            self.guest_client,
            self.authorized_client,
        }
        for user_redirect in user_redirect_post_edit:
            with self.subTest():
                response = user_redirect.get(
                    reverse('post_edit', kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id,
                    }),
                    follow=True
                )
                self.assertRedirects(
                    response,
                    reverse('post', kwargs={
                                        'username': self.user.username,
                                        'post_id': self.post.id
                                    }),
                )

    def test_urls_anonymous_http_status_200(self):
        """Страницы доступны любому пользователю."""
        for reverse_name in self.page_url_names_guest.values():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_urls_correct_template(self):
        """URL-адреса используют соответствующий шаблон."""
        page_url_authorized_client = {
            'new_post.html': reverse('new_post'),
        }
        page_url_authorized_client.update(self.page_url_names_guest)

        for template, reverse_name in page_url_authorized_client.items():
            with self.subTest():
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_edit_post_correct_template(self):
        """URL-адрес /<username>/<post_id>/idit/
        используют соответствующий шаблон.
        """
        response = self.authorized_client_author.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            }),
        )
        self.assertTemplateUsed(response, 'new_post.html')

    def test_page_not_found(self):
        """Возвращает ли сервер код 404 для несущ. страниц"""
        response = self.guest_client.get('/404/')
        self.assertEqual(response.status_code, 404)
