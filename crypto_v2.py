from pyomo.environ import *

# Создание модели
model = ConcreteModel()
model.name = 'CRYPTO'
solver = SolverFactory('cbc', executable="D:\\cbc\\bin\\cbc.exe")

# Экзогенные
model.T = 21  # горизонт планирования
model.J = 12  # количество типов бизнеса
model.n_j = {'Еда': 1000, 'Кино': 5000, 'Аренда': 400}  # средняя аудитория бизнеса j-го типа
model.a_j = Param(model.J)  # среднее число сделок за 1 месяц на 1 юзера в бизнесе j-го типа
model.p_j = Param(model.J)  # средний чек юзера в бизнесе j-го типа
model.d_j = Param(model.J)  # средний размер скидки в бизнесе j-го типа
model.c_j = Param(model.J)  # комиссия платформы для бизнеса j-го типа
model.r_a = Param()  # доходность альтернативных вариантов вложения денег (например, долларовых депозитов)
model.q_pr = Param()  # ставка налога на прибыль
model.q_a = Param()  # ставка налога на альтернативные варианты вложения денег
model.g_jt = Param(model.J, model.T)  # ожидаемый индекс роста количества бизнесов j-го типа в t-м месяце
model.l_t = Param(model.T)  # ожидаемый коэффициент вывода монет в t-м месяце
model.w_v = Param()  # коэффициент вознаграждения валидаторов
model.w_st = Param(model.T)  # доля спекуляторов среди юзеров в t-м месяце
model.v = Param()  # средняя сумма транзакции 1 спекулятора
model.m = Param()  # среднее число транзакций 1 спекулятора за месяц
model.y_t = range(1.005, 1.05)

# Управляемые
model.w_f = Var()  # коэффициент вознаграждения основателей платформы
model.w_r = Var()  # коэффициент резервирования
model.u_ = Var()  # комиссия платформы по переводам между юзерами
model.u_hat = Var()  # комиссия платформы за вывод монет из системы
model.tau = Var()  # длительность периода замарозки
model.h_t = Var()  # процент реинвестирования в t-m периоде


def constraint_curse(model, t):
    return model.k[t + 1] / model.k[t] >= model.y[t]


model.Constraint1 = Constraint(model.T, rule=constraint_curse)

model.Constraint2 = Constraint(expr=0 <= model.w_f <= 1)
model.Constraint3 = Constraint(expr=0 <= model.w_r <= 1)
model.Constraint4 = Constraint(expr=0 <= model.u_hat <= 1)
model.Constraint5 = Constraint(expr=0 <= model.u_tilde <= 1)
model.Constraint6 = Constraint(model.T, expr=0 <= model.h[t] <= 1)
model.Constraint7 = Constraint(expr=model.w_f + model.w_r + model.w_v <= 1)


def objective_rule(model):
    revenue = sum(
        (model.R[t, 'U'] + model.R[t, 'B'] + model.R[t, 'I'] + model.R[t, 'F']) * (1 - model.q_pr) + model.R[t, 'D'] for
        t in model.T)
    cost = sum(model.M[t] * model.z[t] * model.r_a * (1 - model.q_a) for t in model.T)
    profit = revenue - cost
    return profit
