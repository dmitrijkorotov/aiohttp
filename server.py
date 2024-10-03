import json
from aiohttp import web
from models import User, Advertisment, Session, init_orm, engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


# Middleware для глобальной обработки ошибок
@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        # Обработка стандартных HTTP ошибок
        return web.json_response(
            {'status': 'error', 'message': ex.reason},
            status=ex.status,
            content_type="application/json"
        )
    except Exception as ex:
        # Для всех остальных ошибок возвращаем 500
        return web.json_response(
            {'status': 'error', 'message': str(ex)},
            status=500,
            content_type="application/json"
        )


# Middleware для подключения сессии
@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


# Cleanup для инициализации и закрытия базы данных
async def orm_context(app):
    print("START")
    await init_orm()  # Инициализация базы данных
    yield
    await engine.dispose()  # Закрытие соединения с базой данных
    print("FINISH")


# Добавление объекта в сессию
async def add_to_session(obj, session: AsyncSession):
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise web.HTTPConflict(reason=f"{obj.__class__.__name__} already exists")
    return obj


# Получение объекта по ID из сессии
async def get_from_session(session: AsyncSession, model, obj_id: int):
    obj = await session.get(model, obj_id)
    if obj is None:
        raise web.HTTPNotFound(reason=f"{model.__name__} not found")
    return obj


# Базовый класс для CRUD операций
class BaseView(web.View):
    model = None

    @property
    def obj_id(self):
        return int(self.request.match_info['obj_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def get(self):
        obj = await get_from_session(self.session, self.model, self.obj_id)
        return web.json_response(obj.json, dumps=json.dumps)

    async def post(self):
        json_data = await self.request.json()
        obj = self.model(**json_data)
        obj = await add_to_session(obj, self.session)
        return web.json_response(obj.json, dumps=json.dumps)

    async def patch(self):
        obj = await get_from_session(self.session, self.model, self.obj_id)
        json_data = await self.request.json()
        for key, value in json_data.items():
            setattr(obj, key, value)
        await self.session.commit()
        return web.json_response(obj.json, dumps=json.dumps)

    async def delete(self):
        obj = await get_from_session(self.session, self.model, self.obj_id)
        await self.session.delete(obj)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


# Вью для пользователей
class UserView(BaseView):
    model = User


# Вью для объявлений
class AdvertismentView(BaseView):
    model = Advertisment


# Настройка приложения и маршрутов
app = web.Application(middlewares=[error_middleware, session_middleware])

# Добавление Cleanup контекста для инициализации и закрытия базы данных
app.cleanup_ctx.append(orm_context)

# Настройка маршрутов
app.add_routes([
    web.post('/user/', UserView),
    web.get('/user/{obj_id:\d+}/', UserView),
    web.patch('/user/{obj_id:\d+}/', UserView),
    web.delete('/user/{obj_id:\d+}/', UserView),
    web.post('/advertisment/', AdvertismentView),
    web.get('/advertisment/{obj_id:\d+}/', AdvertismentView),
    web.patch('/advertisment/{obj_id:\d+}/', AdvertismentView),
    web.delete('/advertisment/{obj_id:\d+}/', AdvertismentView),
])

# Запуск приложения
if __name__ == '__main__':
    web.run_app(app)
