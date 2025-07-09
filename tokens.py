from itsdangerous import URLSafeTimedSerializer
from keys import secret_key
def token(data,salt):
    serializer=URLSafeTimedSerializer(secret_key)
    data1=serializer.dumps(data,salt=salt)
    return data1