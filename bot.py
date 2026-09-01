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
    await message.answer("Welcome to the Samokat Nutrition Bot! 🍏")
    await message.answer("What is your goal?", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Mass Gain")],
            [types.KeyboardButton(text="Weight Loss")]
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
        builder.add(types.KeyboardButton(text="Skip"))
        await message.answer("List any allergens or foods to avoid (comma separated):",
                            reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(Form.allergens)
    except ValueError:
        await message.answer("Please enter a valid number for your budget.")

@dp.message(StateFilter(Form.allergens))
async def process_allergens(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    allergens = None if message.text.lower() == "skip" else message.text
    
    # Save to database
    database.save_user_data(
        telegram_id=message.from_user.id,
        budget=user_data['budget'],
        allergens=allergens,
        goal=user_data['goal']
    )
    
    await message.answer("Thank you! Your preferences have been saved.",
                        reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

if __name__ == "__main__":
    dp.run_polling(bot)