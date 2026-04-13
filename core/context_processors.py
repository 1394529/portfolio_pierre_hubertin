"""Global context available in all templates."""


def portfolio_globals(request):
    return {
        'OWNER_NAME': 'Pierre Hubertin',
        'OWNER_TITLE': 'Data Analyst — Power BI | SQL | BI Reporting',
        'OWNER_EMAIL': 'pierre.hubertin@example.com',
        'OWNER_GITHUB': 'https://github.com/pierre-hubertin',
        'OWNER_LINKEDIN': 'https://www.linkedin.com/in/pierre-hubertin/',
        'OWNER_LOCATION': 'L\'Ancienne-Lorette, Québec',
        'CV_DOWNLOAD_URL': '/static/cv/pierre_hubertin_cv.pdf',
        'SITE_NAME': 'Pierre Hubertin Portfolio',
    }
