from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that extracts the JWT access token from 
    an HTTP-only cookie instead of the Authorization header.
    """
    def authenticate(self, request):
        """Attempts to authenticate the user using the access token from cookies."""
        header = self.get_header(request)
        
        if header is None:
            raw_token = request.COOKIES.get('access_token') or None
        else:
            raw_token = self.get_raw_token(header)
            
        if raw_token is None:
            return None
            
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
