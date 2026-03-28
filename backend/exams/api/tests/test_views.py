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
