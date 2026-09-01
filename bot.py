from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import database

# Initialize bot and dispatcher
bot = Bot(token="8895014449:AAEQ15yfWcRYILe_20KXCMypEcas-yX_teE")
dp = Dispatcher()

# States
class Form(StatesGroup):
    goal = State()
    budget = State()
    allergens = State()

# Command handlers
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в бота Samokat Nutrition! 🍏")
    await message.answer("Какова ваша цель?", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Набор массы")],
            [types.KeyboardButton(text="Похудение")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await state.set_state(Form.goal)

@dp.message(StateFilter(Form.goal))
async def process_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.answer("What is your daily budget for food? (Enter a number)")
    await state.set_state(Form.budget)

@dp.message(StateFilter(Form.budget))
async def process_budget(message: types.Message, state: FSMContext):
    try:
        budget = float(message.text)
        await state.update_data(budget=budget)
        
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Пропустить"))
        await message.answer("Укажите аллергены или продукты, которые вы не едите (через запятую):",
                            reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(Form.allergens)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для вашего бюджета.")

@dp.message(StateFilter(Form.allergens))
async def process_allergens(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    allergens = None if message.text.lower() == "пропустить" else message.text
    
    # Save to database
    database.save_user_data(
        telegram_id=message.from_user.id,
        budget=user_data['budget'],
        allergens=allergens,
        goal=user_data['goal']
    )
    
    # Call optimizer
    optimized_basket = optimize_basket(
        user_data['budget'],
        allergens
    )
    
    # Format the response
    products_text = '\n'.join(
        f"{i+1}. {p['name']} — {p['price']} руб."
        for i, p in enumerate(optimized_basket['products'])
    )
    
    response = (
        "🎁 Твой калорийный зажор на массу сформирован копейка в копейку!\n"
        "🛒 Список продуктов из Самоката:\n"
        f"{products_text}\n"
        f"💰 Итоговая стоимость: {optimized_basket['total_price']} руб.\n"
        f"📊 Суммарный КБЖУ: Калории: {optimized_basket['total_calories']} ккал | "
        f"Белки: {optimized_basket['total_proteins']} г | "
        f"Жиры: {optimized_basket['total_fats']} г | "
        f"Углеводы: {optimized_basket['total_carbs']} г"
    )
    
    await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

from aiohttp import web
import os

async def handle(request):
    return web.Response(text="Bot is alive")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 10000)))
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())