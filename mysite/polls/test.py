import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_should_display_no_polls_are_available_if_no_question(self):
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")

    def test_should_display_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_should_not_display_future_questions(self):
        create_question(question_text="Past question.", days=-30)
        future_question = create_question(
            question_text="Future question.", days=30
        )
        response = self.client.get(reverse("polls:index"))
        print("check", response.content)
        self.assertTrue(
            future_question not in response.context["latest_question_list"],
        )

    def test_display_multiple_questions_in_index_page(self):
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionModelTests(TestCase):
    def test_was_published_recently_return_false_for_future_Questions(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_return_false_for_question_older_than_a_day(
        self,
    ):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_return_true_for_questions_within_a_day(
        self,
    ):
        time = timezone.now() - datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    class QuestionDetailViewTests(TestCase):
        def test_should_display_404_with_future_question(self):
            future_question = create_question(
                question_text="Future question.", days=5
            )
            url = reverse("polls:detail", args=(future_question.id,))
            response = self.client.get(url)
            self.assertEqual(404, response.status_code)

        def test_should_display_past_questions(self):
            past_question = create_question(
                question_text="Past Question.", days=-5
            )
            url = reverse("polls:detail", args=(past_question.id,))
            response = self.client.get(url)
            self.assertContains(response, past_question.question_text)
