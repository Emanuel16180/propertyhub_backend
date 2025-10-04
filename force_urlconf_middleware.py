# force_urlconf_middleware.py

class ForceURLConfMiddleware:
    """
    Middleware que fuerza el URLconf correcto basado en el tenant.
    Esto es necesario porque TenantMainMiddleware no está funcionando correctamente.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si tenemos un tenant y no es el público, forzar URLconf de tenant
        if hasattr(request, 'tenant'):
            if request.tenant.schema_name != 'public':
                # Es un tenant de clínica, usar config.urls
                request.urlconf = 'config.urls'
                print(f"FORCE URLconf: Tenant {request.tenant.schema_name} -> config.urls")
            else:
                # Es el tenant público, usar config.urls_public
                request.urlconf = 'config.urls_public'
                print(f"FORCE URLconf: Public tenant -> config.urls_public")
        
        response = self.get_response(request)
        return response