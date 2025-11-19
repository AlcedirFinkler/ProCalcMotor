# ThreePhaseCoils/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class CSPMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Basic CSP example (customize as needed)
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        response['Content-Security-Policy'] = csp
        return response