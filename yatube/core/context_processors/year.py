from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    year = datetime.now()
    year = int(year.strftime('%Y'))
    return {
        'year': year,
    }
