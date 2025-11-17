import tkinter as tk
from tkinter import ttk, messagebox
import random

# Создание главного окна приложения
root = tk.Tk()
root.title("Инвестиционный симулятор «Расти с ВТБ»")
root.geometry("900x700")

# Глобальные переменные для хранения состояния игры
initial_capital = 10000  # Начальный капитал
capital = 10000  # Текущий капитал
week = 1  # Текущая неделя
max_week = 12  # Максимальное количество недель в игре
skip_turn = False  # Флаг пропуска хода
total_income = 0  # Общий доход за всю игру
game_over = False  # Флаг окончания игры
auto_invest_mode = False  # Режим автоматического инвестирования
hints_mode = True  # Режим подсказок

# Словарь с инвестиционными инструментами и их параметрами
investments = {"Фонды": {"amount": 0, "return": random.uniform(-5, 15), "risk": "средний",
                         "description": "Диверсифицированные инвестиционные фонды"},
    "Вклады": {"amount": 0, "return": random.uniform(1, 7), "risk": "низкий",
               "description": "Банковские вклады с гарантированной доходностью"},
    "Акции": {"amount": 0, "return": random.uniform(-10, 25), "risk": "высокий",
              "description": "Акции компаний с высокой волатильностью"},
    "Облигации": {"amount": 0, "return": random.uniform(0, 10), "risk": "низкий",
                  "description": "Государственные и корпоративные облигации"},
    "Фонд денежного рынка": {"amount": 0, "return": random.uniform(0.5, 2), "risk": "очень низкий",
                             "description": "Консервативные инструменты денежного рынка"}}

# Список возможных событий в игре
events = ["Рост рынка: все инструменты приносят дополнительно +3%", "Падение рынка: все инструменты теряют -4%",
    "Стабильность: доходность не меняется", "Кризис: высокая волатильность акций",
    "Процентная ставка: вклады и облигации растут +2%", "Инфляция: реальная доходность снижается на 1%",
    "Технологический бум: акции IT-компаний растут +5%", "Экономический спад: все инструменты кроме вкладов теряют -3%"]

# История доходности для анализа
return_history = {}
for instrument in investments:
    return_history[instrument] = []


def start_game():
    """Инициализация новой игры - сброс всех параметров к начальным значениям"""
    global capital, week, skip_turn, initial_capital, total_income, game_over, return_history

    # Установка начальных значений
    initial_capital = 10000
    capital = initial_capital
    week = 1
    skip_turn = False
    total_income = 0
    game_over = False
    return_history = {}
    for instrument in investments:
        return_history[instrument] = []

    # Генерация случайной доходности для всех инструментов
    investments.update({"Фонды": {"amount": 0, "return": random.uniform(-5, 15), "risk": "средний",
                                  "description": "Диверсифицированные инвестиционные фонды"},
        "Вклады": {"amount": 0, "return": random.uniform(1, 7), "risk": "низкий",
                   "description": "Банковские вклады с гарантированной доходностью"},
        "Акции": {"amount": 0, "return": random.uniform(-10, 25), "risk": "высокий",
                  "description": "Акции компаний с высокой волатильностью"},
        "Облигации": {"amount": 0, "return": random.uniform(0, 10), "risk": "низкий",
                      "description": "Государственные и корпоративные облигации"},
        "Фонд денежного рынка": {"amount": 0, "return": random.uniform(0.5, 2), "risk": "очень низкий",
                                 "description": "Консервативные инструменты денежного рынка"}})

    # Обновление интерфейса
    capital_label.config(text=f"Капитал: {capital:.2f} рублей")
    week_label.config(text=f"Неделя: {week}/{max_week}")
    result_label.config(text="")
    event_label.config(text="Событие: -")
    skip_label.config(text="")
    income_label.config(text="Доход с инвестиций: 0.00 рублей", fg="green")
    invest_button.config(state=tk.NORMAL)
    auto_invest_button.config(state=tk.NORMAL)

    # Обновление отображения доходности инструментов
    for instrument in investments:
        return_labels[instrument].config(text=f"{instrument}: {investments[instrument]['return']:.1f}%")
        risk_labels[instrument].config(text=f"Риск: {investments[instrument]['risk']}")

    # Очистка полей ввода
    for instrument in entry_vars:
        entry_vars[instrument].set("")

    # Обновление подсказок
    update_hints()


def check_capital():
    """Проверка наличия капитала - завершение игры если капитал <= 0"""
    global capital, game_over

    if capital <= 0:
        game_over = True
        invest_button.config(state=tk.DISABLED)
        auto_invest_button.config(state=tk.DISABLED)

        # Формирование текста результата
        result_text = f"Игра окончена! Капитал исчерпан!\n"
        result_text += f"Итоговый капитал: {capital:.2f} рублей\n"
        result_text += f"Общий доход с инвестиций: {total_income:.2f} рублей\n"

        if total_income > 0:
            result_text += f"Прибыль: +{total_income:.2f} рублей"
        else:
            result_text += f"Убыток: {total_income:.2f} рублей"

        result_label.config(text=result_text)
        messagebox.showwarning("Банкротство", "Ваш капитал исчерпан! Игра окончена.")
        return True

    return False


def calculate_auto_investments():
    """Автоматическое распределение инвестиций на основе анализа доходности"""
    # Сохраняем текущие доходности для анализа
    current_returns = {}
    for instrument in investments:
        current_returns[instrument] = investments[instrument]["return"]

    # Добавляем текущие доходности в историю
    for instrument in current_returns:
        return_history[instrument].append(current_returns[instrument])

    # Рассчитываем среднюю доходность (используем историю если есть)
    avg_returns = {}
    for instrument in investments:
        if len(return_history[instrument]) > 0:
            # Используем взвешенное среднее, где последние значения имеют больший вес
            history_length = len(return_history[instrument])
            if history_length >= 3:
                recent_returns = return_history[instrument][-3:]
            else:
                recent_returns = return_history[instrument]

            weights = []
            for i in range(len(recent_returns)):
                weights.append(i + 1)  # Веса: 1, 2, 3...

            weighted_sum = 0
            weight_total = 0
            for i in range(len(recent_returns)):
                weighted_sum += recent_returns[i] * weights[i]
                weight_total += weights[i]

            weighted_avg = weighted_sum / weight_total
            avg_returns[instrument] = weighted_avg
        else:
            avg_returns[instrument] = current_returns[instrument]

    # Сортируем инструменты по ожидаемой доходности
    sorted_instruments = []
    for instrument, return_val in avg_returns.items():
        sorted_instruments.append((instrument, return_val))

    def sort_key(item):
        return item[1]

    sorted_instruments.sort(key=sort_key, reverse=True)

    # Базовое распределение по принципу: выше доходность - больше инвестиций
    allocations = {}
    total_positive_return = 0

    # Считаем сумму только положительных доходностей
    for instrument in investments:
        if avg_returns[instrument] > 0:
            total_positive_return += avg_returns[instrument]

    if total_positive_return > 0:
        # Распределяем пропорционально доходности
        for instrument in investments:
            if avg_returns[instrument] > 0:
                base_weight = avg_returns[instrument] / total_positive_return
                # Увеличиваем вес для топ-2 инструментов
                if instrument == sorted_instruments[0][0]:
                    allocations[instrument] = base_weight * 1.8  # Самый высокий вес для лучшего инструмента
                elif instrument == sorted_instruments[1][0]:
                    allocations[instrument] = base_weight * 1.5  # Высокий вес для второго инструмента
                else:
                    allocations[instrument] = base_weight
            else:
                allocations[instrument] = 0.01  # Минимальный вес для отрицательных доходностей
    else:
        # Если все доходности отрицательные, инвестируем в самые безопасные инструменты
        for instrument in investments:
            if instrument == "Вклады" or instrument == "Фонд денежного рынка":
                allocations[instrument] = 0.4
            else:
                allocations[instrument] = 0.05

    # Нормализуем веса чтобы сумма была равна 1
    total_allocation = 0
    for weight in allocations.values():
        total_allocation += weight

    normalized_allocations = {}
    if total_allocation > 0:
        for instrument in allocations:
            normalized_allocations[instrument] = allocations[instrument] / total_allocation
    else:
        # Равномерное распределение если что-то пошло не так
        for instrument in investments:
            normalized_allocations[instrument] = 1.0 / len(investments)

    # Рассчитываем суммы инвестиций (инвестируем 80% капитала для безопасности)
    investment_amounts = {}
    available_capital = capital * 0.8

    for instrument in investments:
        investment_amounts[instrument] = available_capital * normalized_allocations[instrument]

    # Округляем до 2 знаков после запятой
    for instrument in investment_amounts:
        investment_amounts[instrument] = round(investment_amounts[instrument], 2)

    return investment_amounts


def update_hints():
    """Обновление подсказок для игрока"""
    if not hints_mode:
        hints_label.config(text="Режим подсказок отключен")
        return

    # Анализируем текущую ситуацию на рынке
    best_instrument = None
    best_return = -1000
    for instrument in investments:
        if investments[instrument]["return"] > best_return:
            best_return = investments[instrument]["return"]
            best_instrument = instrument

    worst_instrument = None
    worst_return = 1000
    for instrument in investments:
        if investments[instrument]["return"] < worst_return:
            worst_return = investments[instrument]["return"]
            worst_instrument = instrument

    # Формируем подсказки
    hints = []

    # Подсказка по лучшему инструменту
    if investments[best_instrument]["return"] > 5:
        hints.append(f"Рекомендуем: {best_instrument} (доходность: {investments[best_instrument]['return']:.1f}%)")

    # Подсказка по худшему инструменту
    if investments[worst_instrument]["return"] < 0:
        hints.append(f"Избегайте: {worst_instrument} (доходность: {investments[worst_instrument]['return']:.1f}%)")

    # Подсказка по диверсификации
    if week > 3:
        hints.append("Совет: диверсифицируйте инвестиции для снижения риска")

    # Подсказка по рискам
    high_risk_instruments = []
    for inst in investments:
        if investments[inst]["risk"] == "высокий":
            high_risk_instruments.append(inst)

    if len(high_risk_instruments) > 0:
        for high_risk_inst in high_risk_instruments:
            if investments[high_risk_inst]["return"] > 15:
                hints.append(
                    f"Внимание: {high_risk_inst} несут повышенный риск при доходности {investments[high_risk_inst]['return']:.1f}%")

    # Обновляем текст подсказок
    if len(hints) > 0:
        hints_text = "Подсказки:\n" + "\n".join(hints)
    else:
        hints_text = "Подсказки: стабильный рынок, инвестируйте по своему усмотрению"

    hints_label.config(text=hints_text)


def auto_fill_investments():
    """Автоматическое заполнение полей ввода на основе расчета"""
    if not auto_invest_mode:
        return

    try:
        auto_amounts = calculate_auto_investments()
        total_auto = 0

        # Заполняем поля ввода
        for instrument in investments:
            amount = auto_amounts[instrument]
            entry_vars[instrument].set(f"{amount:.2f}")
            total_auto += amount

        # Показываем информацию об автоинвестировании
        auto_info = f"Автораспределение: {total_auto:.2f}₽ из {capital:.2f}₽"
        auto_info_label.config(text=auto_info)

    except Exception as e:
        print(f"Ошибка автоинвестирования: {e}")


def invest_action():
    """Основная функция инвестирования - обработка хода игрока"""
    global capital, week, skip_turn, total_income, initial_capital, game_over

    # Проверка на окончание игры
    if game_over:
        messagebox.showwarning("Игра окончена", "Капитал исчерпан! Начните новую игру.")
        return

    # Обработка пропуска хода
    if skip_turn:
        skip_turn = False
        skip_label.config(text="")
        week += 1
        capital_label.config(text=f"Капитал: {capital:.2f} рублей")
        week_label.config(text=f"Неделя: {week}/{max_week}")

        # Проверка на окончание игры по количеству недель
        if week > max_week:
            end_game()

        # Автозаполнение для следующего хода
        auto_fill_investments()
        return

    # Проверка на окончание игры по количеству недель
    if week > max_week:
        messagebox.showinfo("Игра завершена", f"Игра окончена! Ваш капитал: {capital:.2f} рублей")
        return

    # Автоматическое заполнение полей если включен режим
    if auto_invest_mode:
        auto_fill_investments()

    # Проверка введенных сумм инвестирования
    total_invested = 0
    investment_amounts = {}

    for instrument in investments:
        try:
            amount_str = entry_vars[instrument].get()
            if amount_str == "":
                amount = 0
            else:
                amount = float(amount_str)

            if amount < 0:
                messagebox.showerror("Ошибка", "Нельзя инвестировать отрицательную сумму")
                return

            investment_amounts[instrument] = amount
            total_invested += amount

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа")
            return

    # Проверка достаточности капитала
    if total_invested > capital:
        messagebox.showerror("Ошибка",
                             f"Недостаточно средств для инвестирования. Нужно: {total_invested:.2f}, есть: {capital:.2f}")
        return

    # Применение инвестиций
    for instrument in investments:
        amount = investment_amounts[instrument]
        investments[instrument]["amount"] += amount

    # Расчет дохода за неделю
    weekly_income = 0
    for instrument in investments:
        if investments[instrument]["amount"] > 0:
            profit = investments[instrument]["amount"] * (investments[instrument]["return"] / 100)
            weekly_income += profit

    # Инвестированные средства остаются частью капитала, доход добавляется сверху
    capital += weekly_income
    total_income += weekly_income

    # Проверка что капитал не стал отрицательным
    if capital < 0:
        capital = 0

    # Проверка капитала после инвестирования
    if check_capital():
        return

    # Обновление отображения дохода
    if weekly_income >= 0:
        income_label.config(text=f"Доход с инвестиций: +{weekly_income:.2f} рублей (всего: +{total_income:.2f} рублей)",
                            fg="green")
    else:
        income_label.config(text=f"Доход с инвестиций: {weekly_income:.2f} рублей (всего: {total_income:.2f} рублей)",
                            fg="red")

    # Обработка случайных событий (только если игра не закончилась)
    if week < max_week:
        event = random.choice(events)
        event_label.config(text=f"Событие: {event}")

        # Влияние событий на доходность инструментов
        if "Рост рынка" in event:
            for instrument in investments:
                if instrument != "Вклады" and instrument != "Фонд денежного рынка":
                    new_return = investments[instrument]["return"] + 3
                    if instrument == "Облигации":
                        if new_return < -50:
                            new_return = -50
                        elif new_return > 50:
                            new_return = 50
                    investments[instrument]["return"] = new_return
        elif "Падение рынка" in event:
            for instrument in investments:
                if instrument != "Вклады" and instrument != "Фонд денежного рынка":
                    new_return = investments[instrument]["return"] - 4
                    if instrument == "Облигации":
                        if new_return < -50:
                            new_return = -50
                        elif new_return > 50:
                            new_return = 50
                    investments[instrument]["return"] = new_return
        elif "Кризис" in event:
            new_stocks_return = random.uniform(-20, 30)
            investments["Акции"]["return"] = new_stocks_return
            if random.random() < 0.3:  # 30% шанс пропуска хода при кризисе
                skip_turn = True
                skip_label.config(text="КРИЗИС! Пропуск следующего хода!")
        elif "Процентная ставка" in event:
            investments["Вклады"]["return"] += 2
            new_bonds_return = investments["Облигации"]["return"] + 2
            if new_bonds_return < -50:
                new_bonds_return = -50
            elif new_bonds_return > 50:
                new_bonds_return = 50
            investments["Облигации"]["return"] = new_bonds_return
        elif "Инфляция" in event:
            for instrument in investments:
                investments[instrument]["return"] -= 1
        elif "Технологический бум" in event:
            investments["Акции"]["return"] += 5
            investments["Фонды"]["return"] += 2
        elif "Экономический спад" in event:
            for instrument in investments:
                # Экономический спад не влияет на вклады и фонд денежного рынка
                if instrument != "Вклады" and instrument != "Фонд денежного рынка":
                    investments[instrument]["return"] -= 3

    # Обновление доходности инструментов с учетом волатильности
    for instrument in investments:
        base_return = investments[instrument]["return"]
        if instrument == "Вклады" or instrument == "Фонд денежного рынка":
            investments[instrument]["return"] = base_return + 0.5
        else:
            if instrument == "Акции":
                volatility = 2
            else:
                volatility = 1
            new_return = random.uniform(base_return - volatility, base_return + volatility)
            if instrument == "Облигации":
                if new_return < -50:
                    new_return = -50
                elif new_return > 50:
                    new_return = 50
            elif instrument == "Фонды" and new_return > 20:
                new_return = 20
            investments[instrument]["return"] = new_return

    # Специальное событие для фондов
    if investments["Фонды"]["return"] >= 20:
        if random.random() < 0.4:  # 40% шанс пропуска хода при буме фондов
            skip_turn = True
            skip_label.config(text="БУМ НА РЫНКЕ ФОНДОВ! Пропуск следующего хода!")

    # Переход к следующей неделе
    week += 1

    # Обновление интерфейса
    capital_label.config(text=f"Капитал: {capital:.2f} рублей")
    week_label.config(text=f"Неделя: {week}/{max_week}")

    # Обновление отображения доходности
    for instrument in investments:
        return_labels[instrument].config(text=f"{instrument}: {investments[instrument]['return']:.1f}%")

    # Очистка полей ввода (но не в авторежиме)
    if not auto_invest_mode:
        for instrument in entry_vars:
            entry_vars[instrument].set("")

    # Обновление подсказок
    update_hints()

    # Автозаполнение для следующего хода в авторежиме
    if auto_invest_mode and week <= max_week:
        auto_fill_investments()

    # Проверка на окончание игры
    if week > max_week:
        end_game()


def toggle_auto_invest():
    """Переключение режима автоматического инвестирования"""
    global auto_invest_mode
    auto_invest_mode = not auto_invest_mode

    if auto_invest_mode:
        auto_invest_button.config(text="Автоинвестирование: ВКЛ", bg="lightgreen")
        # Сразу заполняем поля при включении режима
        auto_fill_investments()
    else:
        auto_invest_button.config(text="Автоинвестирование: ВЫКЛ", bg="lightcoral")
        auto_info_label.config(text="")
        # Очищаем поля при выключении авторежима
        for instrument in entry_vars:
            entry_vars[instrument].set("")

    # Обновляем подсказки при изменении режима
    update_hints()


def toggle_hints():
    """Переключение режима подсказок"""
    global hints_mode
    hints_mode = not hints_mode

    if hints_mode:
        hints_button.config(text="Подсказки: ВКЛ", bg="lightblue")
        update_hints()
    else:
        hints_button.config(text="Подсказки: ВЫКЛ", bg="lightcoral")
        hints_label.config(text="Режим подсказок отключен")


def end_game():
    """Завершение игры и вывод итоговых результатов"""
    result_text = f"Игра завершена! Итоговый капитал: {capital:.2f} рублей\n"
    result_text += f"Общий доход с инвестиций: {total_income:.2f} рублей\n"

    if total_income > 0:
        result_text += f"Прибыль: +{total_income:.2f} рублей"
    else:
        result_text += f"Убыток: {total_income:.2f} рублей"

    result_label.config(text=result_text)
    messagebox.showinfo("Игра завершена", result_text)


# Создание элементов интерфейса

# Верхняя панель с информацией
info_frame = tk.Frame(root)
info_frame.pack(pady=10)

# Метка для отображения капитала
capital_label = tk.Label(info_frame, text=f"Капитал: {capital:.2f} рублей", font=("Arial", 14))
capital_label.pack(side=tk.LEFT, padx=10)

# Метка для отображения текущей недели
week_label = tk.Label(info_frame, text=f"Неделя: {week}/{max_week}", font=("Arial", 12))
week_label.pack(side=tk.LEFT, padx=10)

# Фрейм для инструментов и их доходностей
instruments_frame = tk.Frame(root)
instruments_frame.pack(pady=10)

# Метка с заголовком для доходностей
info_label = tk.Label(instruments_frame, text="Доходность инструментов:", font=("Arial", 10, "bold"))
info_label.grid(row=0, column=0, columnspan=len(investments), pady=5)

return_labels = {}
risk_labels = {}
for i, instrument in enumerate(investments):
    frame = tk.Frame(instruments_frame)
    frame.grid(row=1, column=i, padx=10, pady=5)

    labl = tk.Label(frame, text=f"{instrument}: {investments[instrument]['return']:.1f}%", font=("Arial", 9), fg="blue")
    labl.pack()
    return_labels[instrument] = labl

    risk_labl = tk.Label(frame, text=f"Риск: {investments[instrument]['risk']}", font=("Arial", 8), fg="gray")
    risk_labl.pack()
    risk_labels[instrument] = risk_labl

# Фрейм для полей ввода инвестиций
investment_frame = tk.Frame(root)
investment_frame.pack(pady=20)

entry_vars = {}
for i, instrument in enumerate(investments):
    row = tk.Frame(investment_frame)
    row.grid(row=i, column=0, pady=3, sticky="w")

    labl = tk.Label(row, text=f"{instrument}:", width=20, anchor="w")
    labl.pack(side=tk.LEFT)

    entry_var = tk.StringVar()
    entry = tk.Entry(row, textvariable=entry_var, width=12)
    entry.pack(side=tk.LEFT, padx=5)

    desc_label = tk.Label(row, text=investments[instrument]["description"], font=("Arial", 8), fg="darkgray", width=40,
                          anchor="w")
    desc_label.pack(side=tk.LEFT, padx=5)

    entry_vars[instrument] = entry_var

# Метка для информации об автоинвестировании
auto_info_label = tk.Label(root, text="", font=("Arial", 9), fg="purple")
auto_info_label.pack(pady=5)

# Метка для подсказок
hints_label = tk.Label(root, text="Подсказки появятся здесь", font=("Arial", 9), wraplength=600, justify=tk.LEFT,
                       bg="lightyellow", relief=tk.SUNKEN, padx=5, pady=5)
hints_label.pack(pady=10, fill=tk.X, padx=20)

# Метка для отображения событий
event_label = tk.Label(root, text="Событие: -", font=("Arial", 10), wraplength=500)
event_label.pack(pady=5)

# Метка для предупреждений о пропуске хода
skip_label = tk.Label(root, text="", font=("Arial", 10), fg="red")
skip_label.pack()

# Метка для отображения дохода
income_label = tk.Label(root, text="Доход с инвестиций: 0.00 рублей", font=("Arial", 10), fg="green")
income_label.pack()

# Метка для отображения итогов игры
result_label = tk.Label(root, text="", font=("Arial", 12), justify=tk.LEFT)
result_label.pack(pady=10)

# Фрейм для кнопок управления
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Кнопка инвестирования
invest_button = tk.Button(button_frame, text="Инвестировать", command=invest_action, font=("Arial", 12),
                          bg="lightgreen")
invest_button.pack(side=tk.LEFT, padx=10)

# Кнопка начала новой игры
restart_button = tk.Button(button_frame, text="Начать заново", command=start_game, font=("Arial", 12))
restart_button.pack(side=tk.LEFT, padx=10)

# Кнопка переключения автоинвестирования
auto_invest_button = tk.Button(button_frame, text="Автоинвестирование: ВЫКЛ", command=toggle_auto_invest,
                               font=("Arial", 10), bg="lightcoral")
auto_invest_button.pack(side=tk.LEFT, padx=10)

# Кнопка переключения подсказок
hints_button = tk.Button(button_frame, text="Подсказки: ВКЛ", command=toggle_hints, font=("Arial", 10), bg="lightblue")
hints_button.pack(side=tk.LEFT, padx=10)

# Инициализация подсказок
update_hints()

# Запуск главного цикла приложения
root.mainloop()
