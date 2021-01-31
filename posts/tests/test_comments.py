from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Post


class CommentsTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

        self.user_author = get_user_model().objects.create(
            username='StasBasov'
        )

        self.user_authorized = get_user_model().objects.create(
            username='Nikita'
        )
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user_authorized)

        self.post = Post.objects.create(
            text='Текст поста',
            author=self.user_author,
        )

    def test_add_comment_autorized_user(self):
        """Авторизированный пользователь может добавлять комментарии"""
        comment_count = Comment.objects.count()
        comment_text = 'Текст комментария'
        form_data = {
            'text': comment_text,
        }
        response = self.authorized_user.post(
            reverse(
                'add_comment',
                args=[self.post.author.username, self.post.id]
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('post', args=[self.post.author.username, self.post.id])
        )
        self.assertEqual(Comment.objects.count(), comment_count+1)

        new_comment = Comment.objects.latest('id')
        self.assertEqual(new_comment.post, self.post)
        self.assertEqual(new_comment.author, self.user_authorized)
        self.assertEqual(new_comment.text, comment_text)

    def test_add_comments_guest_user(self):
        """Анонимный пользователь не может добавлять комментарии"""
        comment_count = Comment.objects.count()
        comment_text = 'Текст комментария'
        form_data = {
            'text': comment_text,
        }
        response = self.guest_client.post(
            reverse(
                'add_comment',
                args=[self.post.author.username, self.post.id]
            ),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse(
                'add_comment',
                args=[self.post.author.username, self.post.id]
            )
        )
        self.assertEqual(Comment.objects.count(), comment_count)
