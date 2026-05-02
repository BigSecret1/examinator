# Copyright 2026 BigSecret1
#
# Licensed under the Apache License, Version 2.0

from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notes.models import Feedback, FileUploadDailyUsage, Note

from .actions import FunFactAction, NotesAPIAction
from .interfaces import NotesInterface
from .serializers import FeedbackSerializer, NoteListSerializer, NoteSerializer
from .utils import MAX_FILE_SIZE_BYTES, MAX_PAGES


def _truthy(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).lower() in ('1', 'true', 'yes', 'on')


class NotesQuotaAPIView(APIView):
    '''Returns the caller's daily upload quota state.'''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        daily_limit = NotesAPIAction.get_user_daily_limit(request.user)
        usage = FileUploadDailyUsage.objects.filter(
            user=request.user,
            date=today,
        ).first()
        used = usage.count if usage else 0
        return Response({
            'date': today.isoformat(),
            'daily_limit': daily_limit,
            'used': used,
            'remaining': max(daily_limit - used, 0),
            'max_file_size_bytes': MAX_FILE_SIZE_BYTES,
            'max_pages': MAX_PAGES,
        })


class NotesUploadAPIView(APIView):
    '''Accepts a PDF and triggers note generation.'''

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get('file')
        if upload is None:
            return Response(
                {'detail': 'No file uploaded under field "file".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        force_vision = _truthy(request.data.get('force_vision'))

        # Read once into memory; PyMuPDF + Gemini both need bytes.
        pdf_bytes = upload.read()

        result = NotesInterface.generate_notes_from_pdf(
            user=request.user,
            file_name=upload.name,
            file_size=upload.size,
            pdf_bytes=pdf_bytes,
            force_vision=force_vision,
        )

        if result.get('status') == 'success':
            note = Note.objects.get(pk=result['note_id'])
            return Response(
                {
                    'status': 'success',
                    'note': NoteSerializer(note).data,
                    'page_count': result.get('page_count'),
                    'generation_mode': result.get('generation_mode'),
                },
                status=status.HTTP_201_CREATED,
            )

        if result.get('status') == 'rejected':
            return Response(
                {
                    'status': 'rejected',
                    'reason': result.get('reason'),
                    'page_count': result.get('page_count'),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'status': 'error', 'error': result.get('error', 'Generation failed.')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class NotesListAPIView(APIView):
    '''List the caller's notes, newest first.'''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Note.objects.filter(user=request.user).order_by('-created_at')
        return Response({
            'results': NoteListSerializer(qs, many=True).data,
        })


class NoteDetailAPIView(APIView):
    '''Full note (sections, subtopics, key terms, flashcards).'''

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            note = (
                Note.objects
                .prefetch_related('sections__subtopics', 'key_terms', 'flashcards')
                .get(pk=pk, user=request.user)
            )
        except Note.DoesNotExist:
            return Response(
                {'detail': 'Note not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(NoteSerializer(note).data)


class FeedbackAPIView(APIView):
    '''Submit general platform feedback.'''

    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response(
                {'detail': 'message is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        feedback = Feedback.objects.create(
            user=request.user,
            message=message,
        )
        return Response(
            FeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED,
        )


class FunFactAPIView(APIView):
    '''Returns today\'s fun fact for the authenticated user.

    Generated once per user per day using a lightweight Gemini model and
    cached in the DB for subsequent requests.
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        fact = FunFactAction.get_fun_fact(request.user)
        if fact is None:
            return Response(
                {'detail': 'Fun fact unavailable.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'fact': fact})

