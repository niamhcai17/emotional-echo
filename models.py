from database import db
from datetime import datetime

class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_emotion = db.Column(db.Text, nullable=False)
    style = db.Column(db.String(50), nullable=False)
    generated_phrase = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(2), default='es')  # 'es' for Spanish, 'en' for English
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Phrase {self.id}: {self.generated_phrase[:30]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_emotion': self.original_emotion,
            'style': self.style,
            'generated_phrase': self.generated_phrase,
            'language': self.language,
            'created_at': self.created_at.isoformat(),
            'is_favorite': self.is_favorite
        }
