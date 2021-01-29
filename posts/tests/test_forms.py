from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostCreateFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Название группы',
            slug='test-slug',
            description='Описание группы',
        )

        self.post = Post.objects.create(
            text='Текст поста',
            author=self.user,
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        post_new_text = 'Текст поста 2'
        form_data = {
            'group': self.group.id,
            'text': post_new_text,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count+1)

        new_post = Post.objects.latest('id')
        self.assertEqual(new_post.text, post_new_text)
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.author, self.user)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post_new_text = 'Измененный текст'
        form_data = {
            'group': self.group.id,
            'text': post_new_text,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            }),
            data=form_data,
        )
        self.assertRedirects(
            response, reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id,
            })
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, post_new_text)
        self.assertEqual(self.post.group, self.group)
        self.assertEqual(self.post.author, self.user)
