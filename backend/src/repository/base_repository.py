from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundException

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Базовый класс репозитория, инкапсулирующий типовые CRUD операции с БД.
    Обеспечивает повторное использование кода для всех сущностей в проекте.
    Используется как родительский класс для FileRepository и AlertRepository.
    """

    def __init__(self, model: type[T]):
        self.model = model

    async def get_by_id(
        self,
        session: AsyncSession,
        primary_key: Any,
        raise_if_not_found: bool = True,
    ) -> T | None:
        """
        Получить объект по первичному ключу.

        Параметры:
        - **session** (AsyncSession): Сессия БД.
        - **primary_key** (Any): Первичный ключ.
        - **raise_if_not_found** (bool): Бросать ли исключение NotFoundException.

        Возвращает:
        - **T | None**: Объект модели или None.
        """
        obj = await session.get(self.model, primary_key)
        if obj is None and raise_if_not_found:
            raise NotFoundException()
        return obj

    async def create(self, session: AsyncSession, **kwargs) -> T:
        """
        Создать новый объект в базе данных.

        Параметры:
        - **session** (AsyncSession): Сессия БД.
        - **kwargs**: Поля для инициализации модели.

        Возвращает:
        - **T**: Созданный объект с автогенерированными полями.
        """
        obj = self.model(**kwargs)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def update(
        self,
        session: AsyncSession,
        primary_key: Any,
        **kwargs,
    ) -> T | None:
        """
        Обновить поля объекта по первичному ключу.

        Параметры:
        - **session** (AsyncSession): Сессия БД.
        - **primary_key** (Any): Первичный ключ объекта.
        - **kwargs**: Поля для обновления.

        Возвращает:
        - **T | None**: Обновленный объект или None.
        """
        obj = await session.get(self.model, primary_key)
        if obj is None:
            return None
        for field, value in kwargs.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, primary_key: Any) -> bool:
        """
        Удалить объект по его первичному ключу.

        Параметры:
        - **session** (AsyncSession): Сессия БД.
        - **primary_key** (Any): Первичный ключ объекта.

        Возвращает:
        - **bool**: True в случае успешного удаления, иначе False.
        """
        obj = await session.get(self.model, primary_key)
        if obj is None:
            return False
        await session.delete(obj)
        await session.flush()
        return True
