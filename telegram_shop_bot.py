import asyncio
import logging
import sqlite3
from typing import List, Dict, Any

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    CallbackQuery
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ID админа - замените на реальный ID администратора в Telegram
ADMIN_ID = 12345678  # Пример ID

# Инициализация базы данных
def init_db():
    """Инициализация базы данных SQLite и создание необходимых таблиц"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    
    # Создание таблицы товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT
    )
    ''')
    
    # Создание таблицы корзины
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # Вставка примеров товаров, если таблица пуста
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        # Добавляю несколько товаров для тестирования
        sample_products = [
            ('Футболка', 'Хлопковая футболка', 450.0, ''),
            ('Джинсы', 'Классические джинсы', 1200.0, ''),
            ('Кроссовки', 'Спортивные кроссовки', 1800.0, ''),
            ('Куртка', 'Зимняя куртка', 2500.0, ''),
        ]
        cursor.executemany(
            'INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)',
            sample_products
        )
    
    conn.commit()
    conn.close()

# Функции для работы с базой данных товаров
def get_all_products():
    """Получение всех товаров из базы данных"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def get_product(product_id):
    """Получение информации о конкретном товаре по ID"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

# Функции для работы с корзиной
def add_to_cart(user_id, product_id, quantity=1):
    """Добавление товара в корзину пользователя"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже этот товар в корзине
    cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?', 
                   (user_id, product_id))
    existing = cursor.fetchone()
    
    if existing:
        # Если товар уже в корзине, увеличиваем количество
        new_quantity = existing[0] + quantity
        cursor.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?',
                      (new_quantity, user_id, product_id))
    else:
        # Если товара нет в корзине, добавляем новую запись
        cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                      (user_id, product_id, quantity))
    
    conn.commit()
    conn.close()

def get_cart(user_id):
    """Получение содержимого корзины пользователя"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.id, p.name, p.price, c.quantity 
    FROM cart c
    JOIN products p ON c.product_id = p.id
    WHERE c.user_id = ?
    ''', (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return cart_items

def remove_from_cart(user_id, product_id):
    """Удаление товара из корзины пользователя"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?', 
                   (user_id, product_id))
    conn.commit()
    conn.close()

def clear_cart(user_id):
    """Очистка корзины пользователя"""
    conn = sqlite3.connect('shop_bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# Состояния FSM для процесса оформления заказа
class OrderStates(StatesGroup):
    waiting_for_name = State()      # Ожидание ввода имени
    waiting_for_phone = State()     # Ожидание ввода телефона
    waiting_for_address = State()   # Ожидание ввода адреса
    waiting_for_confirmation = State()  # Ожидание подтверждения заказа

# Клавиатуры
def get_main_keyboard():
    """Главная клавиатура с основными кнопками"""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог")],
            [KeyboardButton(text="Корзина")]
        ],
        resize_keyboard=True
    )
    return kb

def get_catalog_keyboard():
    """Клавиатура с товарами из каталога"""
    products = get_all_products()
    keyboard = []
    
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product[1]} - {product[3]} грн.", 
                callback_data=f"view_{product[0]}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_product_keyboard(product_id):
    """Клавиатура для карточки товара"""
    keyboard = [
        [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="Назад к каталогу", callback_data="catalog")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cart_keyboard(user_id):
    """Клавиатура для корзины с товарами пользователя"""
    cart_items = get_cart(user_id)
    keyboard = []
    
    for item in cart_items:
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {item[1]} ({item[3]} шт.)", 
                callback_data=f"remove_{item[0]}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_order_keyboard():
    """Клавиатура для подтверждения заказа"""
    keyboard = [
        [
            InlineKeyboardButton(text="Подтвердить", callback_data="confirm_order"),
            InlineKeyboardButton(text="Отменить", callback_data="cancel_order")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать в наш магазин! Выберите действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "Команды бота:\n"
        "/start - начать работу с ботом\n"
        "/catalog - посмотреть каталог товаров\n"
        "/cart - посмотреть корзину\n"
        "/order - оформить заказ"
    )
    await message.answer(help_text)

@dp.message(F.text == "Каталог")
@dp.message(Command("catalog"))
async def show_catalog(message: types.Message):
    """Обработчик команды просмотра каталога"""
    keyboard = get_catalog_keyboard()
    await message.answer("Выберите товар из каталога:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("view_"))
async def view_product(callback: CallbackQuery):
    """Обработчик просмотра информации о товаре"""
    product_id = int(callback.data.split('_')[1])
    product = get_product(product_id)
    
    if product:
        product_info = (
            f"<b>{product[1]}</b>\n"
            f"{product[2]}\n"
            f"Цена: {product[3]} грн."
        )
        await callback.message.answer(
            product_info, 
            parse_mode="HTML",
            reply_markup=get_product_keyboard(product_id)
        )
    else:
        await callback.message.answer("Товар не найден")
    
    await callback.answer()

@dp.callback_query(F.data.startswith("add_"))
async def add_product_to_cart(callback: CallbackQuery):
    """Обработчик добавления товара в корзину"""
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    
    add_to_cart(user_id, product_id)
    await callback.answer("Товар добавлен в корзину!")

@dp.callback_query(F.data == "catalog")
async def back_to_catalog(callback: CallbackQuery):
    """Обработчик возврата к каталогу"""
    keyboard = get_catalog_keyboard()
    await callback.message.edit_text("Выберите товар из каталога:", reply_markup=keyboard)
    await callback.answer()

@dp.message(F.text == "Корзина")
@dp.message(Command("cart"))
async def show_cart(message: types.Message):
    """Обработчик просмотра корзины"""
    user_id = message.from_user.id
    cart_items = get_cart(user_id)
    
    if not cart_items:
        await message.answer("Ваша корзина пуста")
        return
    
    # Рассчитываем общую стоимость
    total_price = sum(item[2] * item[3] for item in cart_items)
    
    cart_text = "Ваша корзина:\n\n"
    for item in cart_items:
        cart_text += f"{item[1]} - {item[2]} грн. x {item[3]} = {item[2] * item[3]} грн.\n"
    
    cart_text += f"\nИтого: {total_price} грн."
    
    await message.answer(
        cart_text,
        reply_markup=get_cart_keyboard(user_id)
    )

@dp.callback_query(F.data.startswith("remove_"))
async def remove_product_from_cart(callback: CallbackQuery):
    """Обработчик удаления товара из корзины"""
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    
    remove_from_cart(user_id, product_id)
    
    # Обновляем содержимое корзины после удаления
    cart_items = get_cart(user_id)
    if not cart_items:
        await callback.message.edit_text("Ваша корзина пуста")
        await callback.answer()
        return
    
    total_price = sum(item[2] * item[3] for item in cart_items)
    
    cart_text = "Ваша корзина:\n\n"
    for item in cart_items:
        cart_text += f"{item[1]} - {item[2]} грн. x {item[3]} = {item[2] * item[3]} грн.\n"
    
    cart_text += f"\nИтого: {total_price} руб."
    
    await callback.message.edit_text(
        cart_text,
        reply_markup=get_cart_keyboard(user_id)
    )
    await callback.answer("Товар удален из корзины")

@dp.callback_query(F.data == "clear_cart")
async def clear_user_cart(callback: CallbackQuery):
    """Обработчик очистки корзины"""
    user_id = callback.from_user.id
    clear_cart(user_id)
    await callback.message.edit_text("Ваша корзина очищена")
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Обработчик возврата в главное меню"""
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

# Процесс оформления заказа
@dp.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Начало процесса оформления заказа"""
    user_id = callback.from_user.id
    cart_items = get_cart(user_id)
    
    if not cart_items:
        await callback.message.edit_text("Ваша корзина пуста, невозможно оформить заказ")
        await callback.answer()
        return
    
    # Переходим к состоянию ожидания имени
    await state.set_state(OrderStates.waiting_for_name)
    await callback.message.answer("Пожалуйста, введите ваше имя:")
    await callback.answer()

@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка ввода имени пользователя"""
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.waiting_for_phone)
    await message.answer("Пожалуйста, введите ваш номер телефона:")

@dp.message(OrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    """Обработка ввода номера телефона"""
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.waiting_for_address)
    await message.answer("Введите адрес доставки:")

@dp.message(OrderStates.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    """Обработка ввода адреса доставки"""
    user_id = message.from_user.id
    user_data = await state.update_data(address=message.text)
    
    # Получаем содержимое корзины для подтверждения заказа
    cart_items = get_cart(user_id)
    total_price = sum(item[2] * item[3] for item in cart_items)
    
    # Формируем сообщение с данными заказа для подтверждения
    order_text = "Пожалуйста, проверьте данные заказа:\n\n"
    order_text += f"Имя: {user_data['name']}\n"
    order_text += f"Телефон: {user_data['phone']}\n"
    order_text += f"Адрес: {user_data['address']}\n\n"
    
    order_text += "Товары:\n"
    for item in cart_items:
        order_text += f"{item[1]} - {item[2]} грн. x {item[3]} = {item[2] * item[3]} грн.\n"
    
    order_text += f"\nИтого: {total_price} грн."
    
    # Переходим к состоянию подтверждения заказа
    await state.set_state(OrderStates.waiting_for_confirmation)
    await message.answer(
        order_text,
        reply_markup=get_confirm_order_keyboard()
    )

@dp.callback_query(F.data == "confirm_order", OrderStates.waiting_for_confirmation)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения заказа"""
    user_id = callback.from_user.id
    user_data = await state.get_data()
    
    # Получаем содержимое корзины
    cart_items = get_cart(user_id)
    total_price = sum(item[2] * item[3] for item in cart_items)
    
    # Формируем сообщение для отправки администратору
    admin_message = f"Новый заказ от пользователя ID: {user_id}\n\n"
    admin_message += f"Имя: {user_data['name']}\n"
    admin_message += f"Телефон: {user_data['phone']}\n"
    admin_message += f"Адрес: {user_data['address']}\n\n"
    
    admin_message += "Товары:\n"
    for item in cart_items:
        admin_message += f"{item[1]} - {item[2]} грн. x {item[3]} = {item[2] * item[3]} грн.\n"
    
    admin_message += f"\nИтого: {total_price} грн."
    
    # Отправляем заказ администратору
    try:
        await bot.send_message(ADMIN_ID, admin_message)
    except Exception as e:
        logging.error(f"Ошибка при отправке заказа администратору: {e}")
    
    # Очищаем корзину пользователя
    clear_cart(user_id)
    
    # Завершаем машину состояний
    await state.clear()
    
    # Уведомляем пользователя об успешном оформлении заказа
    await callback.message.edit_text(
        "Спасибо за заказ! Мы свяжемся с вами в ближайшее время для подтверждения."
    )
    await callback.answer()

@dp.callback_query(F.data == "cancel_order", OrderStates.waiting_for_confirmation)
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены заказа"""
    # Завершаем машину состояний
    await state.clear()
    
    await callback.message.edit_text(
        "Оформление заказа отменено. Товары остались в вашей корзине."
    )
    await callback.answer()

@dp.message(Command("order"))
async def cmd_order(message: types.Message):
    """Обработчик команды /order - перенаправляет на просмотр корзины для оформления"""
    await show_cart(message)

# Запуск бота
async def main():
    """Основная функция запуска бота"""
    # Инициализируем базу данных
    init_db()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())