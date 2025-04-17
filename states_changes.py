import graphviz

# Цвета для состояний
state_colors = {
    "WAITING": "lightgray",
    "WIN": "lightgreen",
    "CANCELED": "lightcoral"
}

# Цвета для операций (методов)
operation_colors = {
    "betposition_Calculate": "blue",
    "Orders_Betposition_ReCalculate": "darkorange",
    "lineservices_RollbackCalculateOrders": "purple"
}

# Переходы: (откуда, куда, операция, условие)
transitions = [
    ("WAITING", "WIN", "betposition_Calculate", "total_goals > base"),
    ("WAITING", "CANCELED", "betposition_Calculate", "total_goals == base && base.is_integer()"),
    ("WIN", "CANCELED", "Orders_Betposition_ReCalculate", "total_goals == base && base.is_integer()"),
    ("WIN", "WAITING", "lineservices_RollbackCalculateOrders", "total_goals < base && !base.is_integer()"),
    ("CANCELED", "WIN", "Orders_Betposition_ReCalculate", "total_goals > base"),
    ("CANCELED", "WAITING", "lineservices_RollbackCalculateOrders", "total_goals < base"),
]

# Создаём граф с увеличенным разрешением
dot = graphviz.Digraph(format='png')
dot.attr(rankdir='LR', size='14,10')  # Увеличенный размер для размещения условий
dot.attr(dpi='300')  # Увеличиваем разрешение до 300 DPI

# Глобальные настройки графа
dot.attr('node', fontname='Arial', fontsize='14')
dot.attr('edge', fontname='Arial', fontsize='12')
dot.attr('graph', fontname='Arial', fontsize='16')

# Расположение узлов
# Создаем невидимые узлы для контроля расположения
dot.node('invisible1', style='invis')
dot.node('invisible2', style='invis')

# Добавляем узлы (состояния) с прямоугольниками
for state, color in state_colors.items():
    # Делаем WAITING немного больше как центральное состояние
    width = '2.0' if state == 'WAITING' else '1.5'
    height = '1.0' if state == 'WAITING' else '0.8'
    
    dot.node(state, shape='box', style='filled,rounded', fillcolor=color, 
             width=width, height=height, penwidth='1.5', fontcolor='black')

# Устанавливаем ранги для контроля положения
with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('invisible1')
    s.node('WIN')

with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('WAITING')

with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('invisible2')
    s.node('CANCELED')

# Невидимые ребра для позиционирования
dot.edge('invisible1', 'WAITING', style='invis')
dot.edge('WAITING', 'invisible2', style='invis')

# Добавляем переходы с цветными стрелками и условиями
for from_state, to_state, op, condition in transitions:
    color = operation_colors.get(op, "black")
    # Формируем метку с операцией и условием
    label = f"{op}\n[{condition}]"
    dot.edge(from_state, to_state, label=label, color=color, 
             penwidth='1.5', fontcolor=color, arrowsize='1.0')

# Сохраняем схему в файл с высоким разрешением
dot.render("bet_state_transitions", view=True, cleanup=True)
print("Диаграмма сохранена в файл: bet_state_transitions.png")