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
        entry = {'name': '  Sub A  ', 'description': '  Desc  ', 'topic': '  Ancient  ', 'subject': '  History  '}
        result = self.loader.validate(1, entry)
        self.assertEqual(result, ('Sub A', 'Desc', 'ancient', 'history'))
        self.assertEqual(len(self.loader.errors), 0)


class TestSubtopicLoaderPersist(TestCase):
    """Unit tests for SubtopicLoader.persist() — DB fully mocked."""

    @patch('scripts.seed_loader.SubTopic')
    @patch('scripts.seed_loader.Topic')
    def test_persist_creates_subtopic(self, mock_topic_cls, mock_subtopic_cls):
        mock_topic = MagicMock()
        mock_topic.subject.name = 'History'
        mock_topic.name = 'Ancient'
        mock_topic_cls.objects.select_related.return_value.all.return_value = [mock_topic]
        mock_subtopic_cls.objects.update_or_create.return_value = (MagicMock(), True)

        loader = SubtopicLoader.__new__(SubtopicLoader)
        loader.created = 0
        loader.updated = 0
        loader.errors = []

        items = [{'name': 'Sub A', 'description': 'Desc', 'topic': 'ancient', 'subject': 'history'}]
        loader.persist(items)

        self.assertEqual(loader.created, 1)
        self.assertEqual(loader.updated, 0)
        mock_subtopic_cls.objects.update_or_create.assert_called_once()

    @patch('scripts.seed_loader.SubTopic')
    @patch('scripts.seed_loader.Topic')
    def test_persist_records_error_for_missing_topic(self, mock_topic_cls, mock_subtopic_cls):
        mock_topic_cls.objects.select_related.return_value.all.return_value = []

        loader = SubtopicLoader.__new__(SubtopicLoader)
        loader.created = 0
        loader.updated = 0
        loader.errors = []

        items = [{'name': 'Sub A', 'description': 'Desc', 'topic': 'nonexistent', 'subject': 'history'}]
        loader.persist(items)

        self.assertEqual(loader.created, 0)
        self.assertEqual(len(loader.errors), 1)
        self.assertIn('not found in DB', loader.errors[0])
        mock_subtopic_cls.objects.update_or_create.assert_not_called()
