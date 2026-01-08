"""
Tender Tahlil API

Tender shartnomasi va ishtirokchilarni tahlil qilish uchun API endpointlar.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
import PyPDF2
from docx import Document
import tempfile

from core.tender_analyzer import tender_analyzer
from core.services import document_processor

logger = logging.getLogger(__name__)


def extract_text_from_file(file) -> str:
    """Fayldan matn ajratib olish"""
    text = ""
    filename = file.name.lower()
    
    try:
        # Vaqtinchalik faylga saqlash
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        if filename.endswith('.pdf'):
            with open(tmp_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        
        elif filename.endswith('.docx'):
            doc = Document(tmp_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
        
        elif filename.endswith('.txt'):
            with open(tmp_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        else:
            # Oddiy matn sifatida o'qish
            text = file.read().decode('utf-8', errors='ignore')
        
        # Vaqtinchalik faylni o'chirish
        os.unlink(tmp_path)
        
    except Exception as e:
        logger.error(f"Fayl o'qishda xatolik: {str(e)}")
        text = ""
    
    return text


@api_view(['POST'])
def analyze_tender(request):
    """
    Tender shartnomasini tahlil qilish
    
    POST /api/evaluations/analyze-tender/
    
    Body:
        - file: Tender shartnoma fayli (PDF, DOCX, TXT)
        - text: Yoki to'g'ridan-to'g'ri matn
        - metadata: Qo'shimcha ma'lumotlar (JSON)
        - language: Til (uz yoki ru)
    
    Returns:
        - success: bool
        - analysis: Tender tahlili natijalari
    """
    try:
        tender_text = ""
        metadata = {}
        language = request.data.get('language', 'uz')  # Default: O'zbek
        
        # Fayldan yoki matndan olish
        if 'file' in request.FILES:
            file = request.FILES['file']
            tender_text = extract_text_from_file(file)
            metadata['filename'] = file.name
            metadata['file_size'] = file.size
        elif 'text' in request.data:
            tender_text = request.data.get('text', '')
        else:
            error_msg = 'Tender fayli yoki matni talab qilinadi' if language == 'uz' else 'Требуется файл или текст тендера'
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not tender_text.strip():
            error_msg = 'Tender matni bo\'sh' if language == 'uz' else 'Текст тендера пуст'
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Qo'shimcha metadata
        if 'metadata' in request.data:
            try:
                import json
                extra_meta = json.loads(request.data.get('metadata', '{}'))
                metadata.update(extra_meta)
            except:
                pass
        
        metadata['language'] = language
        
        # Tahlil qilish
        result = tender_analyzer.analyze_tender_document(tender_text, metadata)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Tender tahlilida xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def analyze_participant(request):
    """
    Ishtirokchi hujjatlarini tahlil qilish
    
    POST /api/evaluations/analyze-participant/
    
    Body:
        - name: Ishtirokchi nomi
        - file: Ishtirokchi hujjati (PDF, DOCX, TXT)
        - text: Yoki to'g'ridan-to'g'ri matn
        - metadata: Qo'shimcha ma'lumotlar (JSON)
        - language: Til (uz yoki ru)
    
    Returns:
        - success: bool
        - analysis: Ishtirokchi tahlili natijalari
    """
    try:
        language = request.data.get('language', 'uz')
        default_name = 'Noma\'lum ishtirokchi' if language == 'uz' else 'Неизвестный участник'
        participant_name = request.data.get('name', default_name)
        participant_text = ""
        metadata = {'language': language}
        
        # Fayldan yoki matndan olish
        if 'file' in request.FILES:
            file = request.FILES['file']
            participant_text = extract_text_from_file(file)
            metadata['filename'] = file.name
            metadata['file_size'] = file.size
        elif 'text' in request.data:
            participant_text = request.data.get('text', '')
        else:
            error_msg = 'Ishtirokchi fayli yoki matni talab qilinadi' if language == 'uz' else 'Требуется файл или текст участника'
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not participant_text.strip():
            error_msg = 'Ishtirokchi matni bo\'sh' if language == 'uz' else 'Текст участника пуст'
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Qo'shimcha metadata
        if 'metadata' in request.data:
            try:
                import json
                extra_meta = json.loads(request.data.get('metadata', '{}'))
                metadata.update(extra_meta)
            except:
                pass
        
        # Tahlil qilish
        result = tender_analyzer.analyze_participant(
            participant_name, 
            participant_text, 
            metadata
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Ishtirokchi tahlilida xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def compare_participants(request):
    """
    Ishtirokchilarni solishtirish
    
    POST /api/evaluations/compare-participants/
    
    Body:
        - participants: Ishtirokchilar tahlillari ro'yxati
        - language: Til (uz yoki ru)
    
    Returns:
        - success: bool
        - ranking: Reyting bo'yicha saralangan ishtirokchilar
        - winner: G'olib
        - summary: Xulosa
    """
    try:
        participants = request.data.get('participants', [])
        language = request.data.get('language', 'uz')
        
        if not participants:
            error_msg = 'Ishtirokchilar ro\'yxati bo\'sh' if language == 'uz' else 'Список участников пуст'
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = tender_analyzer.compare_participants(participants, language)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Ishtirokchilar solishtirishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def full_analysis(request):
    """
    To'liq tahlil - tender + barcha ishtirokchilar
    
    POST /api/evaluations/full-analysis/
    
    Body:
        - tender_file: Tender shartnoma fayli
        - tender_text: Yoki tender matni
        - participants: [
            {name: "Kompaniya nomi", file: fayl yoki text: matn}
        ]
    
    Returns:
        - success: bool
        - tender_analysis: Tender tahlili
        - participants_analysis: Ishtirokchilar tahlili
        - ranking: Reyting
        - winner: G'olib
        - summary: Xulosa
    """
    try:
        results = {
            'success': True,
            'tender_analysis': None,
            'participants_analysis': [],
            'ranking': [],
            'winner': None,
            'summary': ''
        }
        
        # 1. Tender tahlili
        tender_text = ""
        if 'tender_file' in request.FILES:
            tender_text = extract_text_from_file(request.FILES['tender_file'])
        elif 'tender_text' in request.data:
            tender_text = request.data.get('tender_text', '')
        
        if not tender_text.strip():
            return Response({
                'success': False,
                'error': 'Tender fayli yoki matni talab qilinadi'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tender_result = tender_analyzer.analyze_tender_document(tender_text)
        if not tender_result['success']:
            return Response(tender_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        results['tender_analysis'] = tender_result['analysis']
        
        # 2. Ishtirokchilar tahlili
        participants_data = request.data.get('participants', [])
        
        # Fayllardan ishtirokchilarni olish
        for key in request.FILES:
            if key.startswith('participant_'):
                idx = key.replace('participant_', '').replace('_file', '')
                name = request.data.get(f'participant_{idx}_name', f'Ishtirokchi {idx}')
                file = request.FILES[key]
                text = extract_text_from_file(file)
                
                participant_result = tender_analyzer.analyze_participant(name, text)
                if participant_result['success']:
                    results['participants_analysis'].append(participant_result['analysis'])
        
        # JSON dan ishtirokchilarni olish
        for p in participants_data:
            name = p.get('name', 'Noma\'lum')
            text = p.get('text', '')
            if text:
                participant_result = tender_analyzer.analyze_participant(name, text)
                if participant_result['success']:
                    results['participants_analysis'].append(participant_result['analysis'])
        
        # 3. Solishtirish
        if results['participants_analysis']:
            compare_result = tender_analyzer.compare_participants(results['participants_analysis'])
            if compare_result['success']:
                results['ranking'] = compare_result['ranking']
                results['winner'] = compare_result['winner']
                results['summary'] = compare_result['summary']
        
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"To'liq tahlilda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_tender_requirements(request):
    """
    Joriy tender talablarini olish
    
    GET /api/evaluations/tender-requirements/
    """
    requirements = tender_analyzer.get_tender_requirements()
    tender_info = tender_analyzer.get_tender_info()
    
    return Response({
        'success': True,
        'requirements': requirements,
        'tender_info': tender_info
    })


@api_view(['POST'])
def reset_analysis(request):
    """
    Tahlilni qayta boshlash
    
    POST /api/evaluations/reset/
    """
    global tender_analyzer
    from core.tender_analyzer import TenderAnalyzer
    tender_analyzer = TenderAnalyzer()
    
    return Response({
        'success': True,
        'message': 'Tahlil qayta boshlandi'
    })
