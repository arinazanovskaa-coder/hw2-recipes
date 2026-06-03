import pytest
from recipes import Ingredient, Recipe, ShoppingList, DietaryRecipe


class TestIngredientInit:

    def test_name_saved(self):
        ing = Ingredient("Мука", 500, "г")
        assert ing.name == "Мука"

    def test_quantity_becomes_float(self):
        ing = Ingredient("Яйца", 2, "шт")
        assert ing.quantity == 2.0
        assert type(ing.quantity) is float

    def test_unit_saved(self):
        ing = Ingredient("Молоко", 200, "мл")
        assert ing.unit == "мл"

    def test_zero_quantity_raises(self):
        with pytest.raises(ValueError, match="Количество должно быть положительным"):
            Ingredient("Соль", 0, "г")

    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError):
            Ingredient("Сахар", -5, "г")

    def test_float_quantity_works(self):
        ing = Ingredient("Масло", 0.5, "кг")
        assert ing.quantity == 0.5


class TestIngredientStr:

    def test_basic_format(self):
        ing = Ingredient("Мука", 500, "г")
        assert str(ing) == "Мука: 500.0 г"

    def test_int_shows_as_float(self):
        ing = Ingredient("Яйца", 3, "шт")
        assert str(ing) == "Яйца: 3.0 шт"

    def test_small_float(self):
        ing = Ingredient("Молоко", 0.5, "л")
        assert str(ing) == "Молоко: 0.5 л"


class TestIngredientEq:

    def test_same_name_unit_different_qty_are_equal(self):
        a = Ingredient("Мука", 100, "г")
        b = Ingredient("Мука", 999, "г")
        assert a == b

    def test_different_name_not_equal(self):
        a = Ingredient("Мука", 500, "г")
        b = Ingredient("Сахар", 500, "г")
        assert a != b

    def test_different_unit_not_equal(self):
        a = Ingredient("Мука", 500, "г")
        b = Ingredient("Мука", 500, "кг")
        assert a != b

    def test_not_equal_to_string(self):
        ing = Ingredient("Мука", 500, "г")
        assert ing != "Мука"


class TestRecipeInit:

    def test_title_saved(self):
        r = Recipe("Блины")
        assert r.title == "Блины"

    def test_empty_ingredients_by_default(self):
        r = Recipe("Блины")
        assert r.ingredients == []

    def test_ingredients_passed_in(self):
        flour = Ingredient("Мука", 300, "г")
        r = Recipe("Блины", [flour])
        assert len(r.ingredients) == 1

    def test_two_recipes_dont_share_list(self):
        r1 = Recipe("Блины")
        r2 = Recipe("Пирог")
        r1.add_ingredient(Ingredient("Мука", 300, "г"))
        assert len(r2.ingredients) == 0


class TestAddIngredient:

    def test_adds_new_ingredient(self):
        r = Recipe("Тест")
        r.add_ingredient(Ingredient("Мука", 300, "г"))
        assert len(r.ingredients) == 1

    def test_duplicate_sums_quantity(self):
        r = Recipe("Тест")
        r.add_ingredient(Ingredient("Мука", 300, "г"))
        r.add_ingredient(Ingredient("Мука", 200, "г"))
        assert len(r.ingredients) == 1
        assert r.ingredients[0].quantity == pytest.approx(500.0)

    def test_same_name_different_unit_not_merged(self):
        r = Recipe("Тест")
        r.add_ingredient(Ingredient("Мука", 500, "г"))
        r.add_ingredient(Ingredient("Мука", 1, "кг"))
        assert len(r.ingredients) == 2


class TestRecipeScale:

    def test_returns_new_object(self):
        r = Recipe("Тест", [Ingredient("Мука", 300, "г")])
        scaled = r.scale(2)
        assert scaled is not r

    def test_original_unchanged(self):
        r = Recipe("Тест", [Ingredient("Мука", 300, "г")])
        r.scale(3)
        assert r.ingredients[0].quantity == pytest.approx(300.0)

    def test_quantities_multiplied(self):
        r = Recipe("Тест", [Ingredient("Мука", 300, "г"), Ingredient("Яйца", 2, "шт")])
        scaled = r.scale(2)
        assert scaled.ingredients[0].quantity == pytest.approx(600.0)
        assert scaled.ingredients[1].quantity == pytest.approx(4.0)

    def test_float_ratio(self):
        r = Recipe("Тест", [Ingredient("Мука", 400, "г")])
        scaled = r.scale(0.5)
        assert scaled.ingredients[0].quantity == pytest.approx(200.0)

    def test_zero_ratio_raises(self):
        r = Recipe("Тест", [Ingredient("Мука", 300, "г")])
        with pytest.raises(ValueError):
            r.scale(0)

    def test_negative_ratio_raises(self):
        r = Recipe("Тест", [Ingredient("Мука", 300, "г")])
        with pytest.raises(ValueError):
            r.scale(-2)

    def test_title_preserved(self):
        r = Recipe("Блины", [Ingredient("Мука", 300, "г")])
        assert r.scale(2).title == "Блины"


class TestRecipeLen:

    def test_empty(self):
        assert len(Recipe("Тест")) == 0

    def test_two_ingredients(self):
        r = Recipe("Тест", [Ingredient("Мука", 300, "г"), Ingredient("Молоко", 200, "мл")])
        assert len(r) == 2


@pytest.fixture
def pancakes():
    r = Recipe("Блины")
    r.add_ingredient(Ingredient("Мука", 300, "г"))
    r.add_ingredient(Ingredient("Молоко", 500, "мл"))
    return r


@pytest.fixture
def cake():
    r = Recipe("Пирог")
    r.add_ingredient(Ingredient("Мука", 200, "г"))
    r.add_ingredient(Ingredient("Сахар", 100, "г"))
    return r


class TestShoppingListAddRecipe:

    def test_items_added(self, pancakes):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        assert len(sl._items) == 2

    def test_portions_scale_qty(self, pancakes):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 4)
        flour = [ing for ing, _ in sl._items if ing.name == "Мука"][0]
        assert flour.quantity == pytest.approx(1200.0)

    def test_zero_portions_raises(self, pancakes):
        sl = ShoppingList()
        with pytest.raises(ValueError, match="Количество порций должно быть положительным"):
            sl.add_recipe(pancakes, 0)

    def test_negative_portions_raises(self, pancakes):
        sl = ShoppingList()
        with pytest.raises(ValueError):
            sl.add_recipe(pancakes, -1)


class TestShoppingListRemove:

    def test_removes_recipe_items(self, pancakes):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        sl.remove_recipe("Блины")
        assert len(sl._items) == 0

    def test_only_target_removed(self, pancakes, cake):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        sl.add_recipe(cake, 1)
        sl.remove_recipe("Блины")
        titles = {t for _, t in sl._items}
        assert titles == {"Пирог"}

    def test_missing_recipe_no_crash(self, pancakes):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        sl.remove_recipe("Несуществующий")
        assert len(sl._items) == 2


class TestShoppingListGetList:

    def test_same_ingredient_summed(self, pancakes, cake):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        sl.add_recipe(cake, 1)
        result = sl.get_list()
        flour = next(i for i in result if i.name == "Мука")
        assert flour.quantity == pytest.approx(500.0)

    def test_sorted_by_name(self, pancakes, cake):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        sl.add_recipe(cake, 1)
        result = sl.get_list()
        names = [i.name for i in result]
        assert names == sorted(names)

    def test_returns_ingredient_objects(self, pancakes):
        sl = ShoppingList()
        sl.add_recipe(pancakes, 1)
        for item in sl.get_list():
            assert isinstance(item, Ingredient)

    def test_empty_list(self):
        assert ShoppingList().get_list() == []


class TestShoppingListAdd:

    def test_returns_new_object(self, pancakes, cake):
        sl1 = ShoppingList()
        sl1.add_recipe(pancakes, 1)
        sl2 = ShoppingList()
        sl2.add_recipe(cake, 1)
        merged = sl1 + sl2
        assert merged is not sl1
        assert merged is not sl2

    def test_merged_has_all_items(self, pancakes, cake):
        sl1 = ShoppingList()
        sl1.add_recipe(pancakes, 1)
        sl2 = ShoppingList()
        sl2.add_recipe(cake, 1)
        merged = sl1 + sl2
        assert len(merged._items) == len(sl1._items) + len(sl2._items)

    def test_originals_not_changed(self, pancakes, cake):
        sl1 = ShoppingList()
        sl1.add_recipe(pancakes, 1)
        sl2 = ShoppingList()
        sl2.add_recipe(cake, 1)
        n1, n2 = len(sl1._items), len(sl2._items)
        _ = sl1 + sl2
        assert len(sl1._items) == n1
        assert len(sl2._items) == n2


class TestDietaryRecipe:

    def test_diet_type_stored(self):
        dr = DietaryRecipe("Салат", "веган")
        assert dr.diet_type == "веган"

    def test_inherits_from_recipe(self):
        dr = DietaryRecipe("Салат", "веган", [Ingredient("Помидор", 200, "г")])
        assert dr.title == "Салат"
        assert len(dr.ingredients) == 1

    def test_scale_returns_dietary_recipe(self):
        dr = DietaryRecipe("Салат", "веган", [Ingredient("Помидор", 200, "г")])
        scaled = dr.scale(2)
        assert isinstance(scaled, DietaryRecipe)

    def test_scale_keeps_diet_type(self):
        dr = DietaryRecipe("Салат", "веган", [Ingredient("Помидор", 200, "г")])
        scaled = dr.scale(3)
        assert scaled.diet_type == "веган"

    def test_scale_multiplies(self):
        dr = DietaryRecipe("Салат", "веган", [Ingredient("Помидор", 200, "г")])
        scaled = dr.scale(2)
        assert scaled.ingredients[0].quantity == pytest.approx(400.0)

    def test_str_has_prefix(self):
        dr = DietaryRecipe("Пицца Маргарита", "веган")
        assert str(dr).startswith("[веган] Пицца Маргарита")
