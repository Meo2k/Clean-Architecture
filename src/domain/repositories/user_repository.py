from src.lib.result import Result, Error

from src.domain.entities.user import User
from src.domain.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """ User repository """

    async def find_by_email(self, email: str) -> Result[User, Error]: 
        """ Find a user by email """
        pass 