import json
import itertools
from typing import List, Dict, Optional

# Load product database
with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

def optimize_basket(user_budget: float, allergens: Optional[str]) -> Dict:
    """
    Оптимизирует корзину продуктов
    :param user_budget: бюджет пользователя
    :param allergens: строка аллергенов через запятую
    :return: словарь с оптимальной корзиной и ее характеристиками
    """
    # Фильтрация по аллергенам
    filtered_products = filter_allergens(products, allergens)

    # Поиск оптимальной комбинации
    best_combo = []
    best_protein = 0
    best_price = 0

    # Перебор комбинаций
    for combo in itertools.combinations(filtered_products, len(filtered_products)):
        combo_price = sum(p['price'] for p in combo)
        combo_protein = sum(p['proteins'] for p in combo)

        if combo_price <= user_budget and combo_protein > best_protein:
            best_combo = combo
            best_protein = combo_protein
            best_price = combo_price

    # Возвращаем результат
    total_calories = sum(p['calories'] for p in best_combo)
    total_proteins = sum(p['proteins'] for p in best_combo)
    total_fats = sum(p['fats'] for p in best_combo)
    total_carbs = sum(p['carbs'] for p in best_combo)

    return {
        'products': best_combo,
        'total_price': best_price,
        'total_calories': total_calories,
        'total_proteins': total_proteins,
        'total_fats': total_fats,
        'total_carbs': total_carbs
    }

def filter_allergens(products: List[Dict], allergens: Optional[str]) -> List[Dict]:
    """
    Фильтрует продукты по аллергенам
    :param products: список всех продуктов
    :param allergens: строка аллергенов через запятую
    :return: отфильтрованный список продуктов
    """
    if not allergens:
        return products

    # Разделяем аллергены и нормализуем
    allergen_list = [a.strip().lower() for a in allergens.split(',')]

    # Возвращаем продукты, не содержащие аллергены
    return [p for p in products if not any(
        allergen in p['name'].lower() for allergen in allergen_list
    )]

def format_basket(basket: Dict) -> str:
    """
    Форматирует корзину в читаемый текст
    :param basket: данные корзины
    :return: форматированная строка
    """
    products_text = '\n'.join(
        f"{p['name']} - {p['price']}₽" for p in basket['products']
    )

    return (
        "Оптимальный выбор:\n"
        f"{products_text}\n\n"
        "Итого:\n"
        f"Общая стоимость: {basket['total_price']}₽\n"
        f"Калории: {basket['total_calories']} ккал\n"
        f"Белки: {basket['total_proteins']}г\n"
        f"Жиры: {basket['total_fats']}г\n"
        f"Углеводы: {basket['total_carbs']}г"
    )