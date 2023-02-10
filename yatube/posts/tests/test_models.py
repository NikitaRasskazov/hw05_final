from django.test import TestCase

from ..models import (
    Group,
    Post,
    User,
    Comment,
    Follow,
    NUMBER_OF_CHARACTERS,
    CHARACTERS_IN_COMMENT
)
from posts.tests import const_value


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=const_value.USERNAME_AUTH
        )
        cls.another_author = User.objects.create_user(
            username=const_value.ANOTHER_AUTHOR
        )
        cls.group = Group.objects.create(
            title=const_value.GROUP_TITLE_MAIN,
            slug=const_value.GROUP_SLUG_MAIN,
            description=const_value.GROUP_DESCRIPTION_MAIN,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=const_value.POST_TEXT_MAIN,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text=const_value.COMMENT_TEXT
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.another_author
        )

    def test_models_have_correct_object_names(self):
        str_name_model_post_group = {
            PostModelTest.group.title: str(PostModelTest.group),
            PostModelTest.post.text[
                :NUMBER_OF_CHARACTERS
            ]: str(PostModelTest.post),
            PostModelTest.comment.text[
                :CHARACTERS_IN_COMMENT
            ]: str(self.comment),
            const_value.STR_FOLLOW: str(self.follow),
        }
        for expected, str_name_model in str_name_model_post_group.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, str_name_model)
