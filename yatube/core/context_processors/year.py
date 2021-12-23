from django.utils import timezone


def year(request):
    current_year = int(timezone.now().strftime('%Y'))
    return {
        'year': current_year,
    }
