# handover_app/models.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, name, picture, role='user'):
        self.id = id
        self.email = email
        self.name = name
        self.picture = picture
        self.role = role
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id
    
    @classmethod
    def from_json(cls, data):
        """Create User instance from JSON data."""
        return cls(
            id=data['id'],
            email=data['email'],
            name=data.get('name', data.get('given_name', '') + ' ' + data.get('family_name', '')),
            picture=data.get('picture', ''),
            role=data.get('role', 'user')
        )
    
    def to_json(self):
        """Convert User instance to JSON data."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'role': self.role
        }

