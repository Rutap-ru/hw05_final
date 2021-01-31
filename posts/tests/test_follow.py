from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post


class FollowTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

        self.user_author = get_user_model().objects.create(
            username='StasBasov'
        )

        self.user_subscriber = get_user_model().objects.create(
            username='Nikita'
        )
        self.authorized_subscriber = Client()
        self.authorized_subscriber.force_login(self.user_subscriber)

        self.user_not_subscriber = get_user_model().objects.create(
            username='Andrey'
        )
        self.authorized_not_subscriber = Client()
        self.authorized_not_subscriber.force_login(self.user_not_subscriber)

        Follow.objects.create(
            user=self.user_subscriber,
            author=self.user_author,
        )

        self.post = Post.objects.create(
            text='Текст поста',
            author=self.user_author,
        )

    def test_follow_autorized_user(self):
        """Проверяем подписку пользовател на др. пользователя"""
        count_follow = Follow.objects.filter(
            user=self.user_not_subscriber, author=self.user_author
        ).count()
        response = self.authorized_not_subscriber.get(
            reverse('profile_follow', args=[self.user_author.username]),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('profile', args=[self.user_author.username]),
        )
        new_count = Follow.objects.filter(
            user=self.user_not_subscriber, author=self.user_author
        ).count()
        self.assertEqual(
            new_count,
            count_follow+1,
        )

    def test_unfollow_autorized_user(self):
        """Проверяем отписку пользовател от др. пользователя"""
        count_follow = Follow.objects.filter(
            user=self.user_subscriber, author=self.user_author
        ).count()
        response = self.authorized_subscriber.get(
            reverse('profile_unfollow', args=[self.user_author.username]),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('profile', args=[self.user_author.username]),
        )
        new_count = Follow.objects.filter(
            user=self.user_subscriber, author=self.user_author
        ).count()
        self.assertEqual(
            new_count,
            count_follow-1,
        )

    def test_follow_guest_user(self):
        """Не авторизированный пользователь при подписке
        перенаправится на страницу авторизации
        """
        response = self.guest_client.get(
            reverse('profile_follow', args=[self.user_author.username]),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse(
                'profile_follow',
                args=[self.user_author.username]
            )
        )

    def test_author_new_post_showing_to_subscribers(self):
        """Добавленый пост отображается у подписчиков в ленте"""
        response_subscriber = self.authorized_subscriber.get(
            reverse('follow_index')
        )
        self.assertTrue(
            response_subscriber.context.get('page').object_list
        )
        self.assertEqual(
            response_subscriber.context.get('page').object_list[0], self.post,
        )

    def test_author_new_post_not_showing_to_not_subscribers(self):
        """Добавленый пост не отображается у не подписаных пользователей"""
        response_not_subscriber = self.authorized_not_subscriber.get(
            reverse('follow_index')
        )
        self.assertFalse(
            response_not_subscriber.context.get('page').object_list
        )
