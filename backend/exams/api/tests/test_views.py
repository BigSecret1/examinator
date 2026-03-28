from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.subjects.models import Subject
from exams.models import Exam, ExamSubject


class ExamListViewTests(APITestCase):
    """Tests for GET /api/exams/ (list endpoint)."""

    def setUp(self):
        self.url = reverse('exam-list')
        self.active_exam = Exam.objects.create(
            name='UPSC CSE',
            description='Civil Services Examination',
            country='India',
            conducting_body='UPSC',
            is_active=True,
        )
        self.inactive_exam = Exam.objects.create(
            name='Discontinued Exam',
            is_active=False,
        )

    def test_list_returns_200(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_excludes_inactive_exams(self):
        response = self.client.get(self.url)
        results = response.data['results']
        names = [e['name'] for e in results]
        assert self.active_exam.name in names
        assert self.inactive_exam.name not in names

    def test_list_uses_flat_serializer(self):
        """List response should NOT contain nested exam_subjects."""
        response = self.client.get(self.url)
        results = response.data['results']
        assert 'exam_subjects' not in results[0]

    def test_list_contains_expected_fields(self):
        response = self.client.get(self.url)
        results = response.data['results']
        item = results[0]
        expected_fields = {
            'id', 'name', 'description', 'country',
            'conducting_body', 'frequency', 'official_url',
            'is_active', 'created_at', 'updated_at',
        }
        assert set(item.keys()) == expected_fields

    def test_list_empty_when_no_active_exams(self):
        Exam.objects.update(is_active=False)
        response = self.client.get(self.url)
        assert response.data['results'] == []


class ExamDetailViewTests(APITestCase):
    """Tests for GET /api/exams/<id>/ (detail endpoint)."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Mathematics')
        self.exam = Exam.objects.create(
            name='JEE Advanced',
            description='Engineering entrance exam',
            country='India',
            conducting_body='IIT',
            is_active=True,
        )
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            is_optional=False,
        )
        self.url = reverse('exam-detail', kwargs={'pk': self.exam.pk})

    def test_detail_returns_200(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_detail_contains_exam_subjects(self):
        """Detail response should include nested exam_subjects."""
        response = self.client.get(self.url)
        assert 'exam_subjects' in response.data
        assert len(response.data['exam_subjects']) == 1

    def test_detail_exam_subject_has_nested_subject(self):
        response = self.client.get(self.url)
        exam_subject = response.data['exam_subjects'][0]
        assert 'subject' in exam_subject
        assert exam_subject['subject']['name'] == 'Mathematics'

    def test_detail_exam_subject_has_is_optional(self):
        response = self.client.get(self.url)
        exam_subject = response.data['exam_subjects'][0]
        assert exam_subject['is_optional'] is False

    def test_detail_inactive_exam_returns_404(self):
        self.exam.is_active = False
        self.exam.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_nonexistent_exam_returns_404(self):
        url = reverse('exam-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class ExamReadOnlyTests(APITestCase):
    """Ensure the viewset is read-only (no create/update/delete)."""

    def setUp(self):
        self.list_url = reverse('exam-list')
        self.exam = Exam.objects.create(name='Test Exam', is_active=True)
        self.detail_url = reverse('exam-detail', kwargs={'pk': self.exam.pk})

    def test_post_not_allowed(self):
        response = self.client.post(self.list_url, {'name': 'New Exam'})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_put_not_allowed(self):
        response = self.client.put(self.detail_url, {'name': 'Updated'})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_patch_not_allowed(self):
        response = self.client.patch(self.detail_url, {'name': 'Patched'})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_not_allowed(self):
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class ExamDailyQuestionsAPIViewParamTests(APITestCase):
    """Tests for param validation on GET /api/exams/<id>/daily-questions/."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='NEET', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)
        self.url = reverse(
            'exam-daily-questions', kwargs={'exam_id': self.exam.pk}
        )

    def test_missing_subject_returns_400(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'subject' in response.data

    def test_invalid_subject_type_returns_400(self):
        response = self.client.get(self.url, {'subject': 'abc'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subject_below_min_value_returns_400(self):
        response = self.client.get(self.url, {'subject': 0})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_difficulty_returns_400(self):
        response = self.client.get(
            self.url, {'subject': self.subject.pk, 'difficulty': 'extreme'}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_difficulty_defaults_to_medium(self):
        """When difficulty is omitted, serializer should default to medium."""
        from exams.api.serializers import ExamDailyQuestionsParamsSerializer

        ser = ExamDailyQuestionsParamsSerializer(
            data={'subject': str(self.subject.pk)}
        )
        assert ser.is_valid()
        assert ser.validated_data['difficulty'] == 'medium'

    def test_only_get_method_allowed(self):
        data = {'subject': self.subject.pk}
        assert self.client.post(self.url, data).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert self.client.put(self.url, data).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert self.client.patch(self.url, data).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert self.client.delete(self.url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class ExamDailyQuestionsAPIViewSuccessTests(APITestCase):
    """Tests for successful daily-questions generation."""

    def setUp(self):
        self.subject, _ = Subject.objects.get_or_create(name='Physics')
        self.exam = Exam.objects.create(name='NEET Success', is_active=True)
        ExamSubject.objects.create(exam=self.exam, subject=self.subject)
        self.url = reverse(
            'exam-daily-questions', kwargs={'exam_id': self.exam.pk}
        )

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_returns_200_with_questions(self, mock_generate):
        mock_generate.return_value = {
            'status': 'success',
            'questions': [
                {
                    'text': 'What is Newton\'s first law?',
                    'explanation': 'An object at rest stays at rest.',
                    'answers': [
                        {'text': 'Inertia', 'is_correct': True},
                        {'text': 'Gravity', 'is_correct': False},
                        {'text': 'Friction', 'is_correct': False},
                        {'text': 'Momentum', 'is_correct': False},
                    ],
                },
            ],
        }

        response = self.client.get(
            self.url, {'subject': self.subject.pk, 'difficulty': 'easy'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['text'] == 'What is Newton\'s first law?'

    @patch('exams.api.actions.GeminiClientInterface.generate')
    def test_passes_difficulty_to_action(self, mock_generate):
        mock_generate.return_value = {
            'status': 'success',
            'questions': [
                {
                    'text': 'Hard question',
                    'explanation': 'Explanation',
                    'answers': [
                        {'text': 'A', 'is_correct': True},
                        {'text': 'B', 'is_correct': False},
                        {'text': 'C', 'is_correct': False},
                        {'text': 'D', 'is_correct': False},
                    ],
                },
            ],
        }

        response = self.client.get(
            self.url, {'subject': self.subject.pk, 'difficulty': 'hard'}
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify the prompt included 'hard'
        call_args = mock_generate.call_args
        assert 'hard' in call_args.kwargs['prompt']


class ExamDailyQuestionsAPIViewErrorTests(APITestCase):
    """Tests for error scenarios in daily-questions endpoint."""

    def test_nonexistent_exam_raises_exception(self):
        url = reverse('exam-daily-questions', kwargs={'exam_id': 99999})
        with self.assertRaises(Exam.DoesNotExist):
            self.client.get(url, {'subject': 1})

    def test_inactive_exam_raises_exception(self):
        subject, _ = Subject.objects.get_or_create(name='Physics')
        exam = Exam.objects.create(name='Inactive Exam', is_active=False)
        url = reverse('exam-daily-questions', kwargs={'exam_id': exam.pk})
        with self.assertRaises(Exam.DoesNotExist):
            self.client.get(url, {'subject': subject.pk})


class ExamSubjectsAPIViewTests(APITestCase):
    """Tests for GET /api/exams/<id>/subjects/."""

    def setUp(self):
        self.exam = Exam.objects.create(
            name='NEET Subjects', is_active=True,
        )
        self.physics, _ = Subject.objects.get_or_create(name='Physics')
        self.chemistry, _ = Subject.objects.get_or_create(name='Chemistry')
        self.biology, _ = Subject.objects.get_or_create(name='Biology')
        ExamSubject.objects.create(
            exam=self.exam, subject=self.physics, is_optional=False,
        )
        ExamSubject.objects.create(
            exam=self.exam, subject=self.chemistry, is_optional=False,
        )
        ExamSubject.objects.create(
            exam=self.exam, subject=self.biology, is_optional=True,
        )
        self.url = reverse('exam-subjects', kwargs={'exam_id': self.exam.pk})

    def test_returns_200(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_returns_all_linked_subjects(self):
        response = self.client.get(self.url)
        assert len(response.data) == 3

    def test_response_contains_expected_fields(self):
        response = self.client.get(self.url)
        item = response.data[0]
        assert set(item.keys()) == {'id', 'subject_id', 'subject_name', 'is_optional'}

    def test_subject_id_and_name_are_correct(self):
        response = self.client.get(self.url)
        subject_names = {s['subject_name'] for s in response.data}
        assert subject_names == {'Physics', 'Chemistry', 'Biology'}

    def test_is_optional_flag_is_correct(self):
        response = self.client.get(self.url)
        by_name = {s['subject_name']: s for s in response.data}
        assert by_name['Physics']['is_optional'] is False
        assert by_name['Biology']['is_optional'] is True

    def test_no_topics_or_subtopics_in_response(self):
        """Response should be lightweight — no nested topics."""
        response = self.client.get(self.url)
        item = response.data[0]
        assert 'topics' not in item
        assert 'subtopics' not in item
        assert 'description' not in item

    def test_nonexistent_exam_raises_exception(self):
        url = reverse('exam-subjects', kwargs={'exam_id': 99999})
        with self.assertRaises(Exam.DoesNotExist):
            self.client.get(url)

    def test_inactive_exam_raises_exception(self):
        self.exam.is_active = False
        self.exam.save()
        with self.assertRaises(Exam.DoesNotExist):
            self.client.get(self.url)

    def test_exam_with_no_subjects_returns_empty(self):
        empty_exam = Exam.objects.create(name='Empty Exam', is_active=True)
        url = reverse('exam-subjects', kwargs={'exam_id': empty_exam.pk})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_only_get_method_allowed(self):
        assert self.client.post(self.url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert self.client.put(self.url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert self.client.patch(self.url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert self.client.delete(self.url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
