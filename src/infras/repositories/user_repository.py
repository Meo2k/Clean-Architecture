import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.lib.result import Result, Error, Return, ErrorType

from src.infras.models.user_model import UserModel

from src.domain.entities.user import User
from src.domain.value_objects.user import Email, HashedPassword, Username, PhoneNumber, AvatarUrl
from src.domain.repositories.user_repository import UserRepository


class SQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession): 
        self.session = session
    
    async def find_by_id(self, id: str) -> Result[User, Error]: 
        try: 
            query_id = uuid.UUID(id)
            user_model = await self.session.get(UserModel, query_id)
            
            if user_model is None: 
                return Return.ok(None)

            return Return.ok(self._to_domain(user_model))
        except Exception as e: 
            return Return.err(Error(
                code="find_user_error", 
                message="Failed to find user", 
                error_type=ErrorType.INFRA,
                reason=str(e), 
            ))

    async def find_by_email(self, email: str) -> Result[User, Error]: 
        try: 
            user_model = (await self.session.execute(
                select(UserModel).where(UserModel.email == email)
            )).scalar_one_or_none()
            if user_model is None: 
                return Return.ok(None)
            return Return.ok(self._to_domain(user_model))
        except Exception as e: 
            return Return.err(Error(
                code="find_user_error", 
                message="Failed to find user", 
                error_type=ErrorType.INFRA,
                reason=str(e), 
            ))
    
    async def find_all(self) -> Result[list[User], Error]: 
        try: 
            user_models = await self.session.execute(select(UserModel))
            return Return.ok([self._to_domain(user_model) for user_model in user_models])
        except Exception as e: 
            return Return.err(Error(
                code="find_user_error", 
                message="Failed to find user", 
                error_type=ErrorType.INFRA,
                reason=str(e), 
            ))

    async def delete(self, id: str) -> Result[User, Error]: 
        try: 
            query_id = uuid.UUID(id)
            user_model = await self.session.get(UserModel, query_id)
            if not user_model: 
                return Return.err(Error(
                    code="user_not_found_error", 
                    message="User not found", 
                    reason=f"User with id {id} not found"
                ))
            self.session.delete(user_model)
            return Return.ok(self._to_domain(user_model))
        except Exception as e: 
            return Return.err(Error(
                code="delete_user_error", 
                message="Failed to delete user", 
                error_type=ErrorType.INFRA,
                reason=str(e), 
            ))

    async def save(self, entity: User) -> Result[User, Error]: 
        """ Don't commit session . This is the responsibility of the unit of work """
        try: 
            user_model = self._to_model(entity)
            merged_model = await self.session.merge(user_model)

            return Return.ok(self._to_domain(merged_model))
        except Exception as e: 
            return Return.err(Error(
                code="save_user_error", 
                message="Failed to save user", 
                error_type=ErrorType.INFRA,
                reason=str(e), 
            ))

    @staticmethod
    def _to_domain(user: UserModel) -> User: 
        return User(
            id=str(user.id),
            username=Username(user.username),
            email=Email(user.email),
            password=HashedPassword(user.password),
            status=user.status,
            version=user.version,
            locked_until=user.locked_until,
            failed_login_attempts=user.failed_login_attempts,
            phone_number=PhoneNumber(user.phone_number) if user.phone_number else None,
            avatar_url=AvatarUrl(user.avatar_url) if user.avatar_url else None,
            bio=user.bio,
        )
    
    @staticmethod
    def _to_model(user: User) -> UserModel: 
        return UserModel(
            id=uuid.UUID(user.id),
            username=user.username.value,
            email=user.email.value,
            password=user.password.value,
            status=user.status,
            version=user.version,
            locked_until=user.locked_until,
            failed_login_attempts=user.failed_login_attempts,
            phone_number=user.phone_number.value if user.phone_number else None,
            avatar_url=user.avatar_url.value if user.avatar_url else None,
            bio=user.bio,
        )
    