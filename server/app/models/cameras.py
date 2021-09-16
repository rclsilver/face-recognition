from app.models import Base
from sqlalchemy import Column, String
from urllib.parse import urlparse


class Camera(Base):
    """
    Network camera
    """
    __tablename__ = 'camera'

    label = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)

    @property
    def full_url(self) -> str:
        parsed_url = urlparse(self.url)
        auth_str = ''

        if self.username:
            auth_str = f'{self.username}:'

        if self.password:
            if not auth_str:
                auth_str = f':{self.password}'
            else:
                auth_str = f'{auth_str}{self.password}'

        return '{}://{}{}{}{}{}{}'.format(
            parsed_url.scheme,
            auth_str,
            '@' if auth_str else '',
            parsed_url.netloc,
            parsed_url.path,
            '?' if parsed_url.query else '',
            parsed_url.query
        )
