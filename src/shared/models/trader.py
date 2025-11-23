"""Trader model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Trader:
    """Trader/User domain model."""
    
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    portfolios: List[str] = field(default_factory=list)
    
    def login(self):
        """Record trader login."""
        self.last_login = datetime.now()
    
    def deactivate(self):
        """Deactivate trader account."""
        self.is_active = False
    
    def activate(self):
        """Activate trader account."""
        self.is_active = True
    
    def to_dict(self) -> dict:
        """Convert trader to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'portfolios': self.portfolios,
        }
