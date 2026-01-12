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
from django.http import HttpResponse
import os
import logging
import PyPDF2
from docx import Document
import tempfile
import io
from datetime import datetime

# PDF uchun
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        - tender_data: Tender tahlili (agar server xotirasida yo'q bo'lsa)
    
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
        
        logger.info(f"Ishtirokchi tahlili so'rovi: {participant_name}")
        logger.info(f"tender_requirements mavjud: {len(tender_analyzer.tender_requirements)}")
        
        # Agar tender tahlili yo'q bo'lsa, frontend'dan kelgan ma'lumotni tiklash
        if not tender_analyzer.tender_requirements:
            tender_data_str = request.data.get('tender_data', '')
            logger.info(f"tender_data mavjud: {bool(tender_data_str)}, uzunligi: {len(str(tender_data_str)) if tender_data_str else 0}")
            
            if tender_data_str:
                try:
                    import json
                    tender_data = json.loads(tender_data_str) if isinstance(tender_data_str, str) else tender_data_str
                    logger.info(f"tender_data parse qilindi, kalit: {list(tender_data.keys()) if isinstance(tender_data, dict) else 'dict emas'}")
                    # Tender ma'lumotlarini tiklash
                    restored = tender_analyzer.restore_tender_analysis(tender_data)
                    logger.info(f"Tender tahlili tiklandi: {restored}, requirements: {len(tender_analyzer.tender_requirements)}")
                except Exception as e:
                    logger.warning(f"Tender ma'lumotlarini tiklashda xatolik: {e}")
                    import traceback
                    traceback.print_exc()
        
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


def draw_header_footer(canvas, doc, language='uz'):
    """PDF sahifa header va footer - minimalist"""
    canvas.saveState()
    
    # Header - oddiy chiziq
    canvas.setStrokeColor(colors.Color(0.2, 0.2, 0.2))
    canvas.setLineWidth(0.5)
    canvas.line(1.5*cm, A4[1] - 35, A4[0] - 1.5*cm, A4[1] - 35)
    
    # Brand
    canvas.setFillColor(colors.Color(0.2, 0.2, 0.2))
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(1.5*cm, A4[1] - 28, "TANLOV AI")
    
    # Sana
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(A4[0] - 1.5*cm, A4[1] - 28, datetime.now().strftime('%d.%m.%Y'))
    
    # Footer - oddiy
    canvas.setStrokeColor(colors.Color(0.7, 0.7, 0.7))
    canvas.line(1.5*cm, 35, A4[0] - 1.5*cm, 35)
    
    canvas.setFillColor(colors.Color(0.5, 0.5, 0.5))
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(A4[0] / 2, 20, f"{doc.page}")
    
    canvas.restoreState()


@api_view(['POST'])
def export_pdf(request):
    """
    Tahlil natijalarini PDF formatida eksport qilish - Minimalist dizayn
    """
    try:
        data = request.data
        language = data.get('language', 'uz')
        tender_analysis = data.get('tender_analysis', {})
        ranking = data.get('ranking', [])
        winner = data.get('winner', {})
        summary = data.get('summary', '')
        
        # PDF yaratish
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=50,
            bottomMargin=50
        )
        
        # Ranglar - Minimalist
        DARK = colors.Color(0.15, 0.15, 0.15)
        GRAY = colors.Color(0.4, 0.4, 0.4)
        LIGHT_GRAY = colors.Color(0.95, 0.95, 0.95)
        ACCENT = colors.Color(0.2, 0.5, 0.3)  # Yashil accent
        BORDER = colors.Color(0.85, 0.85, 0.85)
        
        # Stillar - bir xil shrift o'lchamlari
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'Title',
            fontSize=18,
            spaceAfter=20,
            spaceBefore=10,
            alignment=1,
            textColor=DARK,
            fontName='Helvetica-Bold',
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            fontSize=12,
            spaceAfter=12,
            spaceBefore=20,
            textColor=DARK,
            fontName='Helvetica-Bold',
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            fontSize=10,
            spaceAfter=6,
            leading=14,
            textColor=DARK,
            fontName='Helvetica',
        )
        
        small_style = ParagraphStyle(
            'Small',
            fontSize=9,
            spaceAfter=4,
            leading=12,
            textColor=GRAY,
            fontName='Helvetica',
        )
        
        # Elementlar
        elements = []
        
        # Tilga qarab matnlar
        if language == 'uz':
            title = "Tender Tahlili Hisoboti"
            tender_info_title = "Tender ma'lumotlari"
            purpose_label = "Maqsad"
            type_label = "Tur"
            req_count_label = "Talablar"
            ranking_title = "Ishtirokchilar reytingi"
            winner_title = "G'olib"
            score_label = "Ball"
            match_label = "Moslik"
            risk_label = "Xavf"
            strengths_label = "Kuchli tomonlar"
            weaknesses_label = "Kamchiliklar"
            summary_title = "Xulosa"
            risk_levels = {'low': 'Past', 'medium': "O'rta", 'high': 'Yuqori'}
        else:
            title = "Отчет анализа тендера"
            tender_info_title = "Информация о тендере"
            purpose_label = "Цель"
            type_label = "Тип"
            req_count_label = "Требования"
            ranking_title = "Рейтинг участников"
            winner_title = "Победитель"
            score_label = "Балл"
            match_label = "Соответствие"
            risk_label = "Риск"
            strengths_label = "Сильные стороны"
            weaknesses_label = "Слабые стороны"
            summary_title = "Заключение"
            risk_levels = {'low': 'Низкий', 'medium': 'Средний', 'high': 'Высокий'}
        
        # Sarlavha
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 5))
        
        # Chiziq
        elements.append(Table([['']], colWidths=[14*cm], style=TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, BORDER),
        ])))
        elements.append(Spacer(1, 15))
        
        # G'olib - eng yuqorida
        if winner:
            winner_name = winner.get('participant_name', '-')
            winner_score = winner.get('total_weighted_score') or winner.get('overall_match_percentage', 0)
            
            winner_box = Table(
                [[Paragraph(f"<b>{winner_title}:</b> {winner_name}", 
                           ParagraphStyle('W', fontSize=11, textColor=DARK)),
                  Paragraph(f"<b>{winner_score:.0f}%</b>", 
                           ParagraphStyle('W', fontSize=12, textColor=ACCENT, alignment=2))]],
                colWidths=[10*cm, 4*cm]
            )
            winner_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.98, 0.95)),
                ('BOX', (0, 0), (-1, -1), 1, ACCENT),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(winner_box)
            elements.append(Spacer(1, 20))
        
        # Tender ma'lumotlari
        if tender_analysis:
            elements.append(Paragraph(tender_info_title, heading_style))
            
            tender_purpose = tender_analysis.get('tender_purpose', '-')
            if len(tender_purpose) > 100:
                tender_purpose = tender_purpose[:100] + '...'
            
            info_text = f"""
            <b>{purpose_label}:</b> {tender_purpose}<br/>
            <b>{type_label}:</b> {tender_analysis.get('tender_type', '-')}<br/>
            <b>{req_count_label}:</b> {tender_analysis.get('requirements_count', 0)} (majburiy: {tender_analysis.get('mandatory_count', 0)})
            """
            elements.append(Paragraph(info_text, normal_style))
            elements.append(Spacer(1, 15))
        
        # Reyting jadvali
        if ranking:
            elements.append(Paragraph(ranking_title, heading_style))
            
            # Jadval
            header = ['#', 'Ishtirokchi' if language == 'uz' else 'Участник', score_label, match_label, risk_label]
            table_data = [header]
            
            for idx, p in enumerate(ranking, 1):
                score = p.get('total_weighted_score') or p.get('overall_match_percentage', 0)
                risk = risk_levels.get(p.get('risk_level', 'low'), p.get('risk_level', '-'))
                name = p.get('participant_name', '-')
                if len(name) > 30:
                    name = name[:30] + '...'
                
                row = [str(idx), name, f"{score:.0f}%", f"{p.get('overall_match_percentage', 0)}%", risk]
                table_data.append(row)
            
            ranking_table = Table(table_data, colWidths=[1*cm, 7*cm, 2*cm, 2*cm, 2*cm])
            
            table_style_list = [
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, 0), DARK),
                ('TEXTCOLOR', (0, 1), (-1, -1), GRAY),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, 0), 1, DARK),
                ('LINEBELOW', (0, 1), (-1, -2), 0.5, BORDER),
            ]
            
            # G'olib qatori
            if len(table_data) > 1:
                table_style_list.append(('TEXTCOLOR', (0, 1), (-1, 1), DARK))
                table_style_list.append(('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'))
            
            ranking_table.setStyle(TableStyle(table_style_list))
            elements.append(ranking_table)
            elements.append(Spacer(1, 20))
        
        # Har bir ishtirokchi haqida qisqacha
        if ranking:
            for idx, p in enumerate(ranking, 1):
                name = p.get('participant_name', '-')
                score = p.get('total_weighted_score') or p.get('overall_match_percentage', 0)
                
                # Sarlavha
                elements.append(Paragraph(f"<b>{idx}. {name}</b> - {score:.0f}%", 
                               ParagraphStyle('PH', fontSize=10, textColor=DARK, spaceBefore=10, spaceAfter=5)))
                
                # Kuchli tomonlar
                strengths = p.get('strengths', [])
                if strengths:
                    s_text = ', '.join(strengths[:3])
                    if len(s_text) > 100:
                        s_text = s_text[:100] + '...'
                    elements.append(Paragraph(f"+ {s_text}", small_style))
                
                # Kamchiliklar
                weaknesses = p.get('weaknesses', [])
                if weaknesses:
                    w_text = ', '.join(weaknesses[:3])
                    if len(w_text) > 100:
                        w_text = w_text[:100] + '...'
                    elements.append(Paragraph(f"- {w_text}", small_style))
                
                elements.append(Spacer(1, 8))
        
        # Xulosa
        if summary:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(summary_title, heading_style))
            
            # Markdown tozalash
            clean_summary = summary.replace('**', '').replace('*', '').replace('#', '').strip()
            
            # Qisqartirish
            if len(clean_summary) > 1500:
                clean_summary = clean_summary[:1500] + '...'
            
            # Paragraphlarga bo'lish
            for line in clean_summary.split('\n'):
                line = line.strip()
                if line:
                    elements.append(Paragraph(line, small_style))
        
        # PDF yaratish
        doc.build(elements, onFirstPage=lambda c, d: draw_header_footer(c, d, language), 
                  onLaterPages=lambda c, d: draw_header_footer(c, d, language))
        
        # Response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        
        filename = f"tender_tahlil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"PDF eksportda xatolik: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# TAHLIL NATIJALARINI SAQLASH VA OLISH API
# ============================================

from .models import TenderAnalysisResult


@api_view(['POST'])
def save_analysis_result(request):
    """
    Tahlil natijasini bazaga saqlash
    
    POST /api/evaluations/save-result/
    
    Body:
        - tender: Tender tahlili (dict)
        - participants: Ishtirokchilar tahlili (list)
        - ranking: Reyting (list)
        - winner: G'olib (dict)
        - summary: Xulosa (str)
        - language: Til (str)
    """
    try:
        tender = request.data.get('tender', {})
        participants = request.data.get('participants', [])
        ranking = request.data.get('ranking', [])
        winner = request.data.get('winner', {})
        summary = request.data.get('summary', '')
        language = request.data.get('language', 'uz')
        
        # Tender nomi
        tender_name = tender.get('purpose', '') or tender.get('name', '') or 'Nomsiz tender'
        tender_type = tender.get('type', '')
        
        # G'olib ma'lumotlari
        winner_name = winner.get('participant_name', '') if winner else ''
        winner_score = winner.get('total_weighted_score', 0) if winner else 0
        
        # Bazaga saqlash
        result = TenderAnalysisResult.objects.create(
            tender_name=tender_name,
            tender_type=tender_type,
            tender_data=tender,
            participants=participants,
            participant_count=len(participants),
            ranking=ranking,
            winner_name=winner_name,
            winner_score=winner_score,
            summary=summary,
            language=language
        )
        
        return Response({
            'success': True,
            'id': result.id,
            'message': 'Natija muvaffaqiyatli saqlandi'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Natija saqlashda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_analysis_history(request):
    """
    Tahlil tarixini olish
    
    GET /api/evaluations/history/
    
    Query params:
        - limit: Nechta natija (default: 20)
        - offset: Qayerdan boshlash (default: 0)
    """
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        total = TenderAnalysisResult.objects.count()
        results = TenderAnalysisResult.objects.all()[offset:offset + limit]
        
        history = []
        for r in results:
            history.append({
                'id': r.id,
                'date': r.created_at.isoformat(),
                'tender': r.tender_name,
                'tender_type': r.tender_type,
                'winner': r.winner_name,
                'winner_score': r.winner_score,
                'participantCount': r.participant_count,
                'ranking': r.ranking,
                'summary': r.summary,
            })
        
        return Response({
            'success': True,
            'total': total,
            'history': history
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Tarix olishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_analysis_detail(request, pk):
    """
    Bitta tahlil natijasini olish
    
    GET /api/evaluations/history/<id>/
    """
    try:
        result = TenderAnalysisResult.objects.get(pk=pk)
        
        return Response({
            'success': True,
            'result': {
                'id': result.id,
                'date': result.created_at.isoformat(),
                'tender': result.tender_data,
                'tender_name': result.tender_name,
                'tender_type': result.tender_type,
                'participants': result.participants,
                'participantCount': result.participant_count,
                'ranking': result.ranking,
                'winner': result.winner_name,
                'winner_score': result.winner_score,
                'summary': result.summary,
                'language': result.language,
            }
        }, status=status.HTTP_200_OK)
        
    except TenderAnalysisResult.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Natija topilmadi'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Natija olishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_analysis_result(request, pk):
    """
    Tahlil natijasini o'chirish
    
    DELETE /api/evaluations/history/<id>/
    """
    try:
        result = TenderAnalysisResult.objects.get(pk=pk)
        result.delete()
        
        return Response({
            'success': True,
            'message': 'Natija o\'chirildi'
        }, status=status.HTTP_200_OK)
        
    except TenderAnalysisResult.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Natija topilmadi'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Natija o'chirishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_dashboard_stats(request):
    """
    Dashboard uchun statistikalar
    
    GET /api/evaluations/dashboard-stats/
    """
    try:
        from django.db.models import Sum, Avg
        
        total_analyses = TenderAnalysisResult.objects.count()
        total_participants = TenderAnalysisResult.objects.aggregate(
            total=Sum('participant_count')
        )['total'] or 0
        
        # Oxirgi 30 kun
        from datetime import timedelta
        from django.utils import timezone
        
        last_30_days = timezone.now() - timedelta(days=30)
        recent_analyses = TenderAnalysisResult.objects.filter(
            created_at__gte=last_30_days
        ).count()
        
        return Response({
            'success': True,
            'stats': {
                'total_tenders': total_analyses,
                'active_tenders': recent_analyses,
                'total_participants': total_participants,
                'total_evaluations': total_analyses,
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Statistika olishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def download_excel(request):
    """
    Tahlil natijasini Excel formatida yuklab olish
    
    POST /api/evaluations/download-excel/
    """
    import pandas as pd
    from io import BytesIO
    
    try:
        data = request.data
        tender = data.get('tender', {})
        ranking = data.get('ranking', [])
        summary = data.get('summary', '')
        language = data.get('language', 'uz')
        
        if not ranking:
            return Response({
                'success': False,
                'error': 'Ranking ma\'lumotlari yo\'q'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Excel buffer
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Formatlar
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F46E5',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'border': 1,
                'align': 'left',
                'valign': 'vcenter',
                'text_wrap': True
            })
            number_format = workbook.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.0'
            })
            winner_format = workbook.add_format({
                'bold': True,
                'bg_color': '#10B981',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            # === SHEET 1: Reyting ===
            if language == 'uz':
                headers = ['O\'rin', 'Ishtirokchi', 'Umumiy ball', 'Moslik %', 'Narx', 'Xavf', 'Tavsiya']
            else:
                headers = ['Место', 'Участник', 'Общий балл', 'Соответствие %', 'Цена', 'Риск', 'Рекомендация']
            
            ranking_data = []
            for i, p in enumerate(ranking):
                ranking_data.append([
                    i + 1,
                    p.get('participant_name', ''),
                    p.get('total_weighted_score', 0),
                    p.get('overall_match_percentage', 0),
                    p.get('price_analysis', {}).get('proposed_price', 'N/A'),
                    p.get('risk_level', 'N/A'),
                    p.get('recommendation', '')[:100] + '...' if len(p.get('recommendation', '')) > 100 else p.get('recommendation', '')
                ])
            
            df_ranking = pd.DataFrame(ranking_data, columns=headers)
            df_ranking.to_excel(writer, sheet_name='Reyting' if language == 'uz' else 'Рейтинг', index=False, startrow=1)
            
            worksheet_ranking = writer.sheets['Reyting' if language == 'uz' else 'Рейтинг']
            
            # Title
            tender_name = tender.get('tender_purpose', 'Tender tahlili')[:50]
            worksheet_ranking.merge_range('A1:G1', tender_name, header_format)
            
            # Header formatting
            for col_num, value in enumerate(headers):
                worksheet_ranking.write(1, col_num, value, header_format)
            
            # Data formatting
            for row_num, row_data in enumerate(ranking_data):
                for col_num, cell_data in enumerate(row_data):
                    fmt = winner_format if row_num == 0 and col_num in [0, 1, 2] else (number_format if col_num in [2, 3] else cell_format)
                    worksheet_ranking.write(row_num + 2, col_num, cell_data, fmt)
            
            # Column widths
            worksheet_ranking.set_column('A:A', 8)
            worksheet_ranking.set_column('B:B', 25)
            worksheet_ranking.set_column('C:D', 15)
            worksheet_ranking.set_column('E:E', 20)
            worksheet_ranking.set_column('F:F', 12)
            worksheet_ranking.set_column('G:G', 40)
            
            # === SHEET 2: Batafsil ===
            detail_sheet = 'Batafsil' if language == 'uz' else 'Подробно'
            
            if language == 'uz':
                detail_headers = ['Ishtirokchi', 'Kuchli tomonlar', 'Zaif tomonlar']
            else:
                detail_headers = ['Участник', 'Сильные стороны', 'Слабые стороны']
            
            detail_data = []
            for p in ranking:
                strengths = '\n'.join(p.get('strengths', [])[:5])
                weaknesses = '\n'.join(p.get('weaknesses', [])[:5])
                detail_data.append([
                    p.get('participant_name', ''),
                    strengths,
                    weaknesses
                ])
            
            df_detail = pd.DataFrame(detail_data, columns=detail_headers)
            df_detail.to_excel(writer, sheet_name=detail_sheet, index=False)
            
            worksheet_detail = writer.sheets[detail_sheet]
            for col_num, value in enumerate(detail_headers):
                worksheet_detail.write(0, col_num, value, header_format)
            worksheet_detail.set_column('A:A', 25)
            worksheet_detail.set_column('B:C', 50)
            
            # === SHEET 3: Xulosa ===
            summary_sheet = 'Xulosa' if language == 'uz' else 'Итог'
            worksheet_summary = workbook.add_worksheet(summary_sheet)
            
            worksheet_summary.write('A1', 'Tahlil xulosasi' if language == 'uz' else 'Итог анализа', header_format)
            worksheet_summary.merge_range('A2:D20', summary, cell_format)
            worksheet_summary.set_column('A:D', 30)
        
        output.seek(0)
        
        # Response
        filename = f"tender_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Audit log (agar user bo'lsa)
        try:
            from apps.users.models import AuditLog
            if request.user.is_authenticated:
                AuditLog.log(
                    request.user,
                    AuditLog.ActionType.EXCEL_DOWNLOAD,
                    f'Excel yuklab olindi: {tender_name}',
                    request
                )
        except:
            pass
        
        return response
        
    except Exception as e:
        logger.error(f"Excel yaratishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def download_csv(request):
    """
    Tahlil natijasini CSV formatida yuklab olish
    
    POST /api/evaluations/download-csv/
    """
    import csv
    from io import StringIO
    
    try:
        data = request.data
        ranking = data.get('ranking', [])
        language = data.get('language', 'uz')
        
        if not ranking:
            return Response({
                'success': False,
                'error': 'Ranking ma\'lumotlari yo\'q'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # CSV buffer
        output = StringIO()
        
        if language == 'uz':
            headers = ['O\'rin', 'Ishtirokchi', 'Umumiy ball', 'Moslik %', 'Narx', 'Xavf', 'Tavsiya']
        else:
            headers = ['Место', 'Участник', 'Общий балл', 'Соответствие %', 'Цена', 'Риск', 'Рекомендация']
        
        writer = csv.writer(output)
        writer.writerow(headers)
        
        for i, p in enumerate(ranking):
            writer.writerow([
                i + 1,
                p.get('participant_name', ''),
                p.get('total_weighted_score', 0),
                p.get('overall_match_percentage', 0),
                p.get('price_analysis', {}).get('proposed_price', 'N/A'),
                p.get('risk_level', 'N/A'),
                p.get('recommendation', '')
            ])
        
        output.seek(0)
        
        filename = f"tender_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response = HttpResponse(output.read(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"CSV yaratishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_chart_data(request):
    """
    Dashboard grafiklar uchun ma'lumotlar
    
    GET /api/evaluations/chart-data/
    """
    try:
        from django.db.models import Count, Avg
        from django.db.models.functions import TruncDate, TruncMonth
        from datetime import timedelta
        from django.utils import timezone
        
        # Oxirgi 30 kun
        last_30_days = timezone.now() - timedelta(days=30)
        last_12_months = timezone.now() - timedelta(days=365)
        
        # Kunlik tahlillar (oxirgi 30 kun)
        daily_analyses = TenderAnalysisResult.objects.filter(
            created_at__gte=last_30_days
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            avg_score=Avg('winner_score')
        ).order_by('date')
        
        # Oylik tahlillar (oxirgi 12 oy)
        monthly_analyses = TenderAnalysisResult.objects.filter(
            created_at__gte=last_12_months
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            total_participants=Count('participant_count')
        ).order_by('month')
        
        # Tender turlari bo'yicha
        tender_types = TenderAnalysisResult.objects.values(
            'tender_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # G'oliblar ball taqsimoti
        score_distribution = []
        score_ranges = [(0, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
        for low, high in score_ranges:
            count = TenderAnalysisResult.objects.filter(
                winner_score__gte=low,
                winner_score__lt=high
            ).count()
            score_distribution.append({
                'range': f'{low}-{high}',
                'count': count
            })
        
        # Ishtirokchilar soni taqsimoti
        participant_distribution = TenderAnalysisResult.objects.values(
            'participant_count'
        ).annotate(
            count=Count('id')
        ).order_by('participant_count')[:10]
        
        return Response({
            'success': True,
            'charts': {
                'daily_analyses': list(daily_analyses),
                'monthly_analyses': list(monthly_analyses),
                'tender_types': list(tender_types),
                'score_distribution': score_distribution,
                'participant_distribution': list(participant_distribution)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Grafik ma'lumotlari olishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_recent_activities(request):
    """
    So'nggi faoliyatlar (Audit log)
    
    GET /api/evaluations/recent-activities/
    """
    try:
        activities = []
        
        # So'nggi tahlillar
        recent_analyses = TenderAnalysisResult.objects.order_by('-created_at')[:10]
        for analysis in recent_analyses:
            activities.append({
                'type': 'analysis',
                'title': analysis.tender_name[:50] if analysis.tender_name else 'Tender tahlili',
                'description': f"G'olib: {analysis.winner_name} ({analysis.winner_score:.1f} ball)",
                'date': analysis.created_at.isoformat(),
                'participant_count': analysis.participant_count
            })
        
        # Audit loglar (agar mavjud bo'lsa)
        try:
            from apps.users.models import AuditLog
            recent_logs = AuditLog.objects.order_by('-created_at')[:10]
            for log in recent_logs:
                activities.append({
                    'type': 'audit',
                    'title': log.get_action_display(),
                    'description': log.description,
                    'date': log.created_at.isoformat(),
                    'user': log.user.username if log.user else 'System'
                })
        except:
            pass
        
        # Vaqt bo'yicha tartiblash
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return Response({
            'success': True,
            'activities': activities[:20]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Faoliyatlar olishda xatolik: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
