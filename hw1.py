'''
Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары, заказы и пользователи.

    — Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
    — Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
    — Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.
    • Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
    • Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
    • Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена.

Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.
Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.

'''


import databases, uvicorn
import sqlalchemy
import datetime
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "sqlite:///data/database.db" # база данных будет создана в папке проекта
metadata = sqlalchemy.MetaData() # объект MetaData для создания таблицы в базе данных
database = databases.Database(DATABASE_URL) # создание объекта Database для работы с базой данных


'''— Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.'''
'''• Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.'''

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('surname', sqlalchemy.String(50)),
    sqlalchemy.Column('email', sqlalchemy.String(100), unique=True),
    sqlalchemy.Column('password', sqlalchemy.String(50))
) # создание таблицы users в базе данных с полями id, name, surname, email, password и типами данных

'''— Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.'''
'''• Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена.'''
products = sqlalchemy.Table(
    'products',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('product_name', sqlalchemy.String(50)),
    sqlalchemy.Column('description', sqlalchemy.String(250)),
    sqlalchemy.Column('price', sqlalchemy.Float)
) # создание таблицы products в базе данных с полями id, product_name, description, price и типами данных

'''— Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.'''
'''• Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.'''

orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, foreign_key='users.id'),
    sqlalchemy.Column('product_id', sqlalchemy.Integer, foreign_key='products.id'),
    sqlalchemy.Column('order_date', sqlalchemy.DateTime, default=datetime.datetime.now()),
    sqlalchemy.Column('status', sqlalchemy.String(50), default='new')
) # создание таблицы orders в базе данных с полями id, user_id, product_id, order_date, status и типами данных

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={'check_same_thread': False}) # создание объекта Engine
metadata.create_all(engine) # создание таблицы в базе данных

app = FastAPI()

'''Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.'''

class UserIn(BaseModel):
    name: str = Field(max_lenght=50)
    surname: str = Field(max_lenght=50)
    email: str = Field(max_lenght=100)
    password: str = Field(max_lenght=50)

class User(BaseModel):
    id: int
    name: str = Field(max_lenght=50)
    surname: str = Field(max_lenght=50)
    email: str = Field(max_lenght=100)
    password: str = Field(max_lenght=50)

class ProductIn(BaseModel):
    product_name: str = Field(max_lenght=50)
    description: str = Field(max_lenght=250)
    price: float = Field(gt=0)

class Product(BaseModel):
    id: int
    product_name: str = Field(max_lenght=50)
    description: str = Field(max_lenght=250)
    price: float = Field(gt=0)

class OrderIn(BaseModel):
    user_id: int
    product_id: int
    order_date: str = Field(max_lenght=50)
    status: str = Field(max_lenght=50)

class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    order_date: datetime.datetime
    status: str = Field(max_lenght=50)


# Авто заполнение таблицы users:
@app.get('/fake_users/{count}')
async def create_user(count: int):
    for i in range(count):
        query = users.insert().values(name=f'user{i}', surname=f'surname{i}', email=f'email{i}@test.ru', password=f'password{i}')
        await database.execute(query)
    return {'message': f'{count} users created'}

# Авто заполнение таблицы products:
@app.get('/fake_products/{count}')
async def create_product(count: int):
    for i in range(count):
        query = products.insert().values(product_name=f'product{i}', description=f'description{i}', price=f'{i+1}00.00')
        await database.execute(query)
    return {'message': f'{count} products created'}

# Авто заполнение таблицы orders:
@app.get('/fake_orders/{count}')
async def create_order(count: int):
    for i in range(count):
        query = orders.insert().values(user_id=i+1, product_id=i+1, order_date=datetime.datetime.now(), status='new')
        await database.execute(query)
    return {'message': f'{count} orders created'}

'''Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API.'''

# CREATE - создание записи
@app.post('/users/', response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(name=user.name, surname=user.surname, email=user.email, password=user.password)
    last_record_id = await database.execute(query) # ожидание выполнения запроса к базе данных
    return {**user.dict(), 'id': last_record_id}

# READ - чтение записи
@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

# CREATE - создание записи
@app.post('/products/', response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(product_name=product.product_name, description=product.description, price=product.price)
    last_record_id = await database.execute(query)
    return {**product.dict(), 'id': last_record_id}

# READ - чтение записи
@app.get('/products/', response_model=List[Product])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)

# CREATE - создание записи
@app.post('/orders/', response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(user_id=order.user_id, product_id=order.product_id, order_date=datetime.datetime.now(), status=order.status)
    last_record_id = await database.execute(query)
    return {**order.dict(), 'id': last_record_id}

# READ - чтение записи
@app.get('/orders/', response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.put('/users/{user_id}', response_model=User)
async def update_user(user_id: int, user: UserIn):
    query = users.update().where(users.c.id == user_id).values(name=user.name, surname=user.surname, email=user.email, password=user.password)
    await database.execute(query)
    return {**user.dict(), 'id': user_id}

@app.put('/products/{product_id}', response_model=Product)
async def update_product(product_id: int, product: ProductIn):
    query = products.update().where(products.c.id == product_id).values(product_name=product.product_name, description=product.description, price=product.price)
    await database.execute(query)
    return {**product.dict(), 'id': product_id}

@app.put('/orders/{order_id}', response_model=Order)
async def update_order(order_id: int, order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(user_id=order.user_id, product_id=order.product_id, order_date=datetime.datetime.now(), status=order.status)
    await database.execute(query)
    return {**order.dict(), 'id': order_id}

@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': f'user with id {user_id} deleted'}

@app.delete('/products/{product_id}')
async def delete_product(product_id: int):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': f'product with id {product_id} deleted'}

@app.delete('/orders/{order_id}')
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': f'order with id {order_id} deleted'}



@app.on_event("startup") # событие startup, которое происходит при запуске приложения
async def startup():
    await database.connect() # подключение к базе данных

@app.on_event("shutdown")  # app.on_event - это декоратор, события
async def shutdown():
    await database.disconnect() # отключение от базы данных


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

