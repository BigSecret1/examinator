# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock

import yaml

from scripts.seed_loader import read_file, SubtopicLoader


class TestReadFile(TestCase):
    """Unit tests for the read_file function."""

    @patch.object(Path, 'exists', return_value=False)
    def test_raises_when_file_not_found(self, _):
        with self.assertRaises(FileNotFoundError):
            read_file(Path('/fake/path.yaml'))

    @patch.object(Path, 'exists', return_value=True)
    @patch('builtins.open', mock_open(read_data=''))
    def test_raises_when_yaml_empty(self, _):
        with self.assertRaises(ValueError):
            read_file(Path('/fake/path.yaml'))

    @patch.object(Path, 'exists', return_value=True)
    @patch('builtins.open', mock_open(read_data='key: value'))
    def test_raises_when_yaml_root_not_list(self, _):
        with self.assertRaises(ValueError):
            read_file(Path('/fake/path.yaml'))

    @patch.object(Path, 'exists', return_value=True)
    def test_returns_parsed_list(self, _):
        yaml_content = yaml.dump([{'name': 'Test'}])
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            result = read_file(Path('/fake/path.yaml'))
        self.assertEqual(result, [{'name': 'Test'}])


class TestSubtopicLoaderValidate(TestCase):
    """Unit tests for SubtopicLoader.validate()."""

    def setUp(self):
        self.loader = SubtopicLoader.__new__(SubtopicLoader)
        self.loader.errors = []

    def test_missing_name_returns_none(self):
        result = self.loader.validate(1, {'topic': 'ancient', 'subject': 'history'})
        self.assertIsNone(result)
        self.assertEqual(len(self.loader.errors), 1)
        self.assertIn('missing "name"', self.loader.errors[0])

    def test_missing_topic_returns_none(self):
        result = self.loader.validate(1, {'name': 'Test', 'subject': 'history'})
        self.assertIsNone(result)
        self.assertIn('missing "topic"', self.loader.errors[0])

    def test_missing_subject_returns_none(self):
        result = self.loader.validate(1, {'name': 'Test', 'topic': 'ancient'})
        self.assertIsNone(result)
        self.assertIn('missing "subject"', self.loader.errors[0])

    def test_valid_entry_returns_tuple(self):
        entry = {
            'name': '  Sub A  ',
            'description': '  Desc  ',
            'topic': '  Ancient  ',
            'subject': '  History  '
        }
        result = self.loader.validate(1, entry)
        self.assertEqual(result, ('Sub A', 'Desc', 'ancient', 'history'))
        self.assertEqual(len(self.loader.errors), 0)


class TestSubtopicLoaderFindSubject(TestCase):
    """Unit tests for SubtopicLoader.find_subject()."""

    @patch('scripts.seed_loader.Subject')
    def test_returns_subject_when_exists(self, mock_subject_cls):
        mock_subject = MagicMock()
        mock_subject_cls.objects.filter.return_value.first.return_value = mock_subject

        loader = SubtopicLoader.__new__(SubtopicLoader)
        result = loader.find_subject('history')

        self.assertEqual(result, mock_subject)
        mock_subject_cls.objects.filter.assert_called_once_with(name__iexact='history')

    @patch('scripts.seed_loader.Subject')
    def test_returns_none_when_not_exists(self, mock_subject_cls):
        mock_subject_cls.objects.filter.return_value.first.return_value = None

        loader = SubtopicLoader.__new__(SubtopicLoader)
        result = loader.find_subject('nonexistent')

        self.assertIsNone(result)


class TestSubtopicLoaderFindTopic(TestCase):
    """Unit tests for SubtopicLoader.find_topic()."""

    @patch('scripts.seed_loader.Topic')
    def test_returns_topic_when_exists(self, mock_topic_cls):
        mock_subject = MagicMock()
        mock_topic = MagicMock()
        mock_topic_cls.objects.filter.return_value.first.return_value = mock_topic

        loader = SubtopicLoader.__new__(SubtopicLoader)
        result = loader.find_topic(mock_subject, 'ancient')

        self.assertEqual(result, mock_topic)
        mock_topic_cls.objects.filter.assert_called_once_with(
            subject=mock_subject, name__iexact='ancient'
        )

    @patch('scripts.seed_loader.Topic')
    def test_returns_none_when_not_exists(self, mock_topic_cls):
        mock_subject = MagicMock()
        mock_topic_cls.objects.filter.return_value.first.return_value = None

        loader = SubtopicLoader.__new__(SubtopicLoader)
        result = loader.find_topic(mock_subject, 'nonexistent')

        self.assertIsNone(result)


class TestSubtopicLoaderPersist(TestCase):
    """Unit tests for SubtopicLoader.persist() — DB fully mocked."""

    @patch('scripts.seed_loader.SubTopic')
    def test_persist_creates_subtopic(self, mock_subtopic_cls):
        mock_subject = MagicMock()
        mock_topic = MagicMock()
        mock_subtopic_cls.objects.update_or_create.return_value = (MagicMock(), True)

        loader = SubtopicLoader.__new__(SubtopicLoader)
        loader.created = 0
        loader.updated = 0
        loader.errors = []
        loader.find_subject = MagicMock(return_value=mock_subject)
        loader.find_topic = MagicMock(return_value=mock_topic)

        items = [{
            'name': 'Sub A',
            'description': 'Desc',
            'topic': 'ancient',
            'subject': 'history'
        }]
        loader.persist(items)

        self.assertEqual(loader.created, 1)
        self.assertEqual(loader.updated, 0)
        loader.find_subject.assert_called_once_with('history')
        loader.find_topic.assert_called_once_with(mock_subject, 'ancient')
        mock_subtopic_cls.objects.update_or_create.assert_called_once()

    @patch('scripts.seed_loader.SubTopic')
    def test_persist_records_error_for_missing_subject(self, mock_subtopic_cls):
        loader = SubtopicLoader.__new__(SubtopicLoader)
        loader.created = 0
        loader.updated = 0
        loader.errors = []
        loader.find_subject = MagicMock(return_value=None)

        items = [{
            'name': 'Sub A',
            'description': 'Desc',
            'topic': 'ancient',
            'subject': 'nonexistent'
        }]
        loader.persist(items)

        self.assertEqual(loader.created, 0)
        self.assertEqual(len(loader.errors), 1)
        self.assertIn('subject "nonexistent" not found in DB', loader.errors[0])
        mock_subtopic_cls.objects.update_or_create.assert_not_called()

    @patch('scripts.seed_loader.SubTopic')
    def test_persist_records_error_for_missing_topic(self, mock_subtopic_cls):
        mock_subject = MagicMock()

        loader = SubtopicLoader.__new__(SubtopicLoader)
        loader.created = 0
        loader.updated = 0
        loader.errors = []
        loader.find_subject = MagicMock(return_value=mock_subject)
        loader.find_topic = MagicMock(return_value=None)

        items = [{
            'name': 'Sub A',
            'description': 'Desc',
            'topic': 'nonexistent',
            'subject': 'history'
        }]
        loader.persist(items)

        self.assertEqual(loader.created, 0)
        self.assertEqual(len(loader.errors), 1)
        self.assertIn('topic "nonexistent" under subject "history" not found in DB', loader.errors[0])
        mock_subtopic_cls.objects.update_or_create.assert_not_called()
