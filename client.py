import aiohttp
import asyncio

BASE_URL = 'http://localhost:8080'


async def create_user(session, name, email, password):
    url = f'{BASE_URL}/user/'
    user_data = {
        "name": name,
        "email": email,
        "password": password
    }
    async with session.post(url, json=user_data) as response:
        if response.status == 200:
            user = await response.json()
            print(f"User created: {user}")
        else:
            error = await response.json()
            print(f"Error creating user: {error}")


async def create_advertisment(session, title, description, user_id):
    url = f'{BASE_URL}/advertisment/'
    ad_data = {
        "title": title,
        "description": description,
        "user_id": user_id
    }
    async with session.post(url, json=ad_data) as response:
        if response.status == 200:
            advertisment = await response.json()
            print(f"Advertisment created: {advertisment}")
        else:
            error = await response.json()
            print(f"Error creating advertisment: {error}")


async def get_user(session, user_id):
    url = f'{BASE_URL}/user/{user_id}/'
    async with session.get(url) as response:
        if response.status == 200:
            user = await response.json()
            print(f"User details: {user}")
        else:
            error = await response.json()
            print(f"Error getting user: {error}")


async def update_user(session, user_id, new_data):
    url = f'{BASE_URL}/user/{user_id}/'
    async with session.patch(url, json=new_data) as response:
        if response.status == 200:
            user = await response.json()
            print(f"User updated: {user}")
        else:
            error = await response.json()
            print(f"Error updating user: {error}")


async def delete_user(session, user_id):
    url = f'{BASE_URL}/user/{user_id}/'
    async with session.delete(url) as response:
        if response.status == 200:
            print(f"User {user_id} deleted")
        else:
            error = await response.json()
            print(f"Error deleting user: {error}")


async def main():
    async with aiohttp.ClientSession() as session:
        # Создаем пользователя
        await create_user(session, name="Test_1", email="test@example.com", password="password123")

        # Создаем новое объявление
        await create_advertisment(session, title="New Car", description="Selling my car", user_id=1)

        # Получаем пользователя
        await get_user(session, user_id=1)

        # Обновляем данные пользователя
        await update_user(session, user_id=1, new_data={"name": "Test_2", "email": "Test_2@example.com"})

        # Удаляем пользователя
        # await delete_user(session, user_id=1)


if __name__ == '__main__':
    asyncio.run(main())
