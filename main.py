from typing import Literal, Tuple, Dict, List
import pandas as pd

# Типы допустимых состояний
State = Literal["WAITING", "WIN", "CANCELED"]
Transition = Tuple[State, str]

# Логика перехода состояния
def calculate_transition(cur_state: State, base: float, score1: int, score2: int) -> Transition:
    total_goals = score1 + score2

    if cur_state == "WIN":
        if total_goals > base:
            return ("WIN", "WIN")
        elif total_goals == base and base.is_integer():
            return ("WIN", "Orders_Betposition_ReCalculate, CANCELED")
        elif total_goals < base and not base.is_integer():
            return ("WIN", "lineservices_RollbackCalculateOrders, WAITING")
        else:
            return ("WIN", "WIN")

    if cur_state == "CANCELED":
        if total_goals > base:
            return ("CANCELED", "Orders_Betposition_ReCalculate, WIN")
        elif total_goals < base:
            return ("CANCELED", "lineservices_RollbackCalculateOrders, WAITING")
        else:
            return ("CANCELED", "CANCELED")

    if cur_state == "WAITING":
        if total_goals > base:
            return ("WAITING", "betposition_Calculate, WIN")
        elif total_goals == base and base.is_integer():
            return ("WAITING", "betposition_Calculate, CANCELED")
        else:
            return ("WAITING", "WAITING")

    return (cur_state, cur_state)

# Сценарии изменения счёта
score_table = [
    (0, 0),
    (1, 0),
    (1, 1),
    (2, 0),
    (2, 1),
    (2, 0),
    (1, 0),
    (1, 1),
    (2, 1)
]

# Начальные состояния для всех тоталов
states: Dict[float, State] = {
    0.5: "WAITING",
    1.0: "WAITING",
    1.5: "WAITING",
    2.0: "WAITING"
}

# История переходов
transitions_log: List[Dict[str, str]] = []

# Генерация строк
for s1, s2 in score_table:
    row = {"score": f"{s1}:{s2}"}
    for base in [0.5, 1.0, 1.5, 2.0]:
        cur_state = states[base]
        from_state, to_state = calculate_transition(cur_state, base, s1, s2)

        # Выделяем операцию и новое состояние
        if "," in to_state:
            operation, next_state = to_state.split(",")
            operation = operation.strip()
            next_state = next_state.strip()
        else:
            operation = "-"
            next_state = to_state.strip()

        # Записываем переход и операцию
        row[f"TБ{base}"] = f"{from_state} → {next_state}"
        row[f"op_TБ{base}"] = operation

        # Обновляем состояние
        if next_state in {"WAITING", "WIN", "CANCELED"}:
            states[base] = next_state
        else:
            raise ValueError(f"Недопустимое состояние: {next_state}")
    transitions_log.append(row)

# Преобразуем в таблицу
df_transitions = pd.DataFrame(transitions_log)

# Показать таблицу (или сохранить)
print(df_transitions.to_string(index=False))
df_transitions.to_csv("state_transitions.csv", index=False)
