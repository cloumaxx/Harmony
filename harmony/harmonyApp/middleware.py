# middleware.py

class UserContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nombre = request.session.get('nombre')
        request.nombre = nombre
        response = self.get_response(request)
        return response
