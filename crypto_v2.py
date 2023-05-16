from pyomo.environ import *

# Создание модели
model = ConcreteModel()
model.name = 'CRYPTO'
solver = SolverFactory('ipopt', executable="C:\\Users\\User\\Desktop\\ipopt.exe")

# Экзогенные
model.T = Set(initialize=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])  # период
model.J = Set(initialize=[1, 2, 3])
model.n_j = {1: 1000, 2: 5000, 3: 400}  # средняя аудитория бизнеса j-го типа
model.a_j = {1: 4.5, 2: 1, 3: 3}  # среднее число сделок за 1 месяц на 1 юзера в бизнесе j-го типа
model.p_j = {1: 10, 2: 5, 3: 40}  # средний чек юзера в бизнесе j-го типа
model.d_j = {1: 5, 2: 5, 3: 5}  # средний размер скидки в бизнесе j-го типа
model.c_j = {1: 1.5, 2: 1.5, 3: 1.5}  # комиссия платформы для бизнеса j-го типа
model.r_a = 4  # доходность альтернативных вариантов вложения денег (например, долларовых депозитов)
model.q_pr = 24  # ставка налога на прибыль
model.q_a = 4  # ставка налога на альтернативные варианты вложения денег
model.g_jt = Param(model.J, model.T, initialize={(1, 1): 1.03},
                   default=0)  # ожидаемый индекс роста количества бизнесов j-го типа в t-м месяце
model.l_t = Param(model.T, initialize={1: 20, 2: 20}, default=0)  # ожидаемый коэффициент вывода монет в t-м месяце;
model.w_v = 5  # коэффициент вознаграждения валидаторов
model.w_st = 12  # доля спекуляторов среди юзеров в t-м месяце ??????
model.v = 100  # средняя сумма транзакции 1 спекулятора
model.m = 1  # среднее число транзакций 1 спекулятора за месяц
model.y_t = 1.005

# Управляемые
model.w_f = Var(within=NonNegativeReals, bounds=(0, 1), initialize=0)
model.w_r = Var(initialize=1, bounds=(0, 1), within=NonNegativeIntegers)  # коэффициент резервирования
model.w_nu = Var(initialize=1, bounds=(0, 1), within=NonNegativeIntegers)
model.u_ = Var(initialize=1, bounds=(0, 1), within=NonNegativeIntegers)  # комиссия платформы по переводам между юзерами
model.u_hat = Var(initialize=1, bounds=(0, 1),
                  within=NonNegativeIntegers)  # комиссия платформы за вывод монет из системы
model.tau = Var(initialize=2, within=NonNegativeIntegers)  # длительность периода замарозки
model.h_t = Var(initialize=1, bounds=(0, 1), within=NonNegativeIntegers)  # процент реинвестирования в t-m периоде

model.B_j0 = 5


def B_jt_initialize_rule(model, j, t):
    return model.B_j0 * model.g_jt[j, t]


model.B_jt = Var(model.J, model.T, initialize=B_jt_initialize_rule)


def N_t_initialize_rule(model, t):
    if t == 1:
        return 0 + sum(model.B_jt[j, t] * model.n_j[j] for j in model.J)
    else:
        return model.N_t[t - 1] + sum(model.B_jt[j, t] * model.n_j[j] for j in model.J)


model.N_t = Var(model.T, initialize=N_t_initialize_rule)


def S_jt_initialize_rule(model, j, t):
    return model.B_jt[j, t] * model.a_j[j]


model.S_jt = Var(model.J, model.T, initialize=S_jt_initialize_rule)


def M_t_plus_rule(model, t):
    return sum(model.S_jt[j, t] * model.p_j[j] * (1 - model.w_r - model.w_nu - model.w_f) for j in model.J)


model.M_t_plus = Expression(model.T, rule=M_t_plus_rule)


def M_t_minus_initialize_rule(model, t):
    return model.M_t_plus[t] * (1 - 1 / model.tau) * model.l_t[t]


model.M_t_minus = Var(model.T, initialize=M_t_minus_initialize_rule)


def M_t_initialize_rule(model, t):
    if t == 1:
        return 0 + model.M_t_plus[t] - model.M_t_minus[t]
    else:
        return model.M_t[t - 1] + model.M_t_plus[t] - model.M_t_minus[t]


model.M_t = Var(model.T, initialize=M_t_initialize_rule)


def R_t_U_initialize_rule(model, t):
    return sum(model.S_jt[j, t] * model.p_j[j] * model.d_j[j] * model.w_f for j in model.J)


model.R_t_U = Var(model.T, initialize=R_t_U_initialize_rule)


def R_t_B_initialize_rule(model, t):
    return sum(model.S_jt[j, t] * model.p_j[j] * (1 - model.d_j[j]) * model.c_j[j] for j in model.J)


model.R_t_B = Var(model.T, initialize=R_t_B_initialize_rule)


def R_t_I_initialize_rule(model, t):
    return model.N_t[t] * model.w_st * model.v * model.u_


model.R_t_I = Var(model.T, initialize=R_t_I_initialize_rule)


def R_t_F_initialize_rule(model, t):
    return model.M_t_plus[t] * (1 - 1 / model.tau) * model.l_t[t] * model.u_hat


model.R_t_F = Var(model.T, initialize=R_t_F_initialize_rule)


def R_t_D_initialize_rule(model, t):
    return model.M_t[t] * (1 / model.tau) * model.r_a * (1 - model.q_a)


model.R_t_D = Var(model.T, initialize=R_t_D_initialize_rule)


def k_t_initialize_rule(model, t):
    return (model.M_t[t] + (
            (model.R_t_U[t] + model.R_t_B[t] + model.R_t_I[t] + model.R_t_F[t]) * (1 - model.q_pr) + model.R_t_D[
        t]) * model.h_t) / model.M_t[t]


model.k_t = Var(model.T, initialize=k_t_initialize_rule)


def K_t_initialize_rule(model, t):
    return model.M_t[t] * model.k_t[t]


model.K_t = Var(model.T, initialize=K_t_initialize_rule)


def obj_rule(model):
    return sum(
        (model.R_t_U[t] + model.R_t_B[t] + model.R_t_I[t] + model.R_t_F[t]) * (1 - model.q_pr) + model.R_t_D[t] for t in
        model.T) * (1 - model.h_t)


model.obj = Objective(rule=obj_rule, sense=maximize)


def rate_grow_constraint(model, t):
    if t == model.T.at(-1):
        return (model.k_t[t] / model.k_t[t]) >= model.y_t
    else:
        return (model.k_t[t + 1] / model.k_t[t]) >= model.y_t


def w_f_economic_constraint_rule(model):
    return model.w_f <= 1


def w_r_economic_constraint_rule(model):
    return model.w_r <= 1


def u__economic_constraint_rule(model):
    return model.u_ <= 1


def u_hat_economic_constraint_rule(model):
    return model.u_hat <= 1


def h_t_economic_constraint_rule(model):
    return model.h_t <= 1


def sum_constraint(model):
    return model.w_f + model.w_r + model.w_nu <= 1


model.sumconstraint = Constraint(rule=sum_constraint)
model.w_f_constraint = Constraint(rule=w_f_economic_constraint_rule)
model.w_r_constraint = Constraint(rule=w_r_economic_constraint_rule)
model.u__constraint = Constraint(rule=u__economic_constraint_rule)
model.u_hat_constraint = Constraint(rule=u_hat_economic_constraint_rule)
model.h_t_constraint = Constraint(rule=h_t_economic_constraint_rule)
model.rate_constraint = Constraint(model.T, rule=rate_grow_constraint)

results = solver.solve(model)  # оптимизация модели
