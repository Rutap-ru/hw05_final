from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class PageCacheTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

        self.user = get_user_model().objects.create(username='StasBasov')

        Post.objects.create(
            text='Текст поста 1',
            author=self.user,
        )

    def test_index_page_post_cache(self):
        """Проверяем кеширование вывода постов на главной странице"""
        response = self.guest_client.get(reverse('index'))
        Post.objects.create(
            text='Текст поста 2',
            author=self.user,
        )
        response2 = self.guest_client.get(reverse('index'))
        self.assertEqual(str(response.content), str(response2.content))
        cache.clear()
        response3 = self.guest_client.get(reverse('index'))
        self.assertNotEqual(str(response.content), str(response3.content))
