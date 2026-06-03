class Ingredient:

    def __init__(self, name, quantity, unit):
        self.name = name
        self.quantity = quantity
        self.unit = unit

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        val = float(value)
        if val <= 0:
            raise ValueError("Количество должно быть положительным")
        self._quantity = val

    def __str__(self):
        return f"{self.name}: {self.quantity} {self.unit}"

    def __repr__(self):
        return f"Ingredient('{self.name}', {self.quantity}, '{self.unit}')"

    def __eq__(self, other):
        if not isinstance(other, Ingredient):
            return NotImplemented
        return self.name == other.name and self.unit == other.unit
    


class Recipe:

    def __init__(self, title, ingredients=None):
        self.title = title
        if ingredients is None:
            self.ingredients = []
        else:
            self.ingredients = list(ingredients)

    def add_ingredient(self, ingredient):
        for ing in self.ingredients:
            if ing == ingredient:
                ing.quantity += ingredient.quantity
                return
        self.ingredients.append(ingredient)

    @staticmethod
    def is_valid_ratio(ratio):
        if isinstance(ratio, bool):
            return False
        return isinstance(ratio, (int, float)) and ratio > 0

    def scale(self, ratio):
        if not self.is_valid_ratio(ratio):
            raise ValueError("Коэффициент должен быть числом больше нуля")

        new_ingredients = []
        for ing in self.ingredients:
            new_ingredients.append(
                Ingredient(ing.name, ing.quantity * ratio, ing.unit)
            )
        return Recipe(self.title, new_ingredients)

    def __len__(self):
        return len(self.ingredients)

    def __str__(self):
        if not self.ingredients:
            return f"{self.title}\n  (ингредиентов нет)"
        parts = [self.title]
        for ing in self.ingredients:
            parts.append(f"  - {ing}")
        return "\n".join(parts)

class ShoppingList:

    def __init__(self):
        self._items = []

    def add_recipe(self, recipe, portions):
        if portions <= 0:
            raise ValueError("Количество порций должно быть положительным")

        scaled = recipe.scale(portions)
        for ing in scaled.ingredients:
            self._items.append((ing, recipe.title))

    def remove_recipe(self, title):
        self._items = [(ing, t) for ing, t in self._items if t != title]

    def get_list(self):
        totals = {}
        for ing, _ in self._items:
            key = (ing.name, ing.unit)
            if key in totals:
                totals[key] += ing.quantity
            else:
                totals[key] = ing.quantity

        result = []
        for (name, unit), qty in totals.items():
            result.append(Ingredient(name, qty, unit))

        result.sort(key=lambda x: x.name)
        return result

    def __add__(self, other):
        if not isinstance(other, ShoppingList):
            return NotImplemented
        combined = ShoppingList()
        combined._items = self._items.copy() + other._items.copy()
        return combined
    
class DietaryRecipe(Recipe):

    def __init__(self, title, diet_type, ingredients=None):
        super().__init__(title, ingredients)
        self.diet_type = diet_type

    def scale(self, ratio):
        base = super().scale(ratio)
        return DietaryRecipe(base.title, self.diet_type, base.ingredients)

    def __str__(self):
        parent = super().__str__()
        lines = parent.split("\n")
        lines[0] = f"[{self.diet_type}] {lines[0]}"
        return "\n".join(lines)
