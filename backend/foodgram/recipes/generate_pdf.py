import os
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def generate_pdf(queryset):
    """Создание PDF файла для отправки пользователю"""
    buffer = BytesIO()
    pdfmetrics.registerFont(
        TTFont(
            "LatoLight", os.path.join(
                settings.BASE_DIR, 'recipes', 'font', 'lato-light.ttf'
            )
        )
    )

    pdf_file = canvas.Canvas(buffer, bottomup=0)
    pdf_file.setFont("LatoLight", 25)

    y = 150
    pdf_file.drawString(40, 100, text='Cписок покупок:')
    for obj in queryset:
        text = (f'{obj["ingredient__name"].capitalize()} '
                f'--> {obj["quantity"]} '
                f'{obj["ingredient__measurement_unit"]}')
        pdf_file.drawString(100, y, text=text)
        y += 20

    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf;  charset=utf-8')
    response['Content-Disposition'] = (
        'attachment; filename="list_in_shop.pdf"'
    )
    response.write(pdf)
    return response
