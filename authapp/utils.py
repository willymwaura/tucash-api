# utils.py

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        # Add other user data as needed
    }
