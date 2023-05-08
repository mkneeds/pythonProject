import openpyxl
from pyomo.environ import *
from pyomo.opt import SolverFactory
import pandas as pd

data = pd.read_excel("D:\\marketing.xlsx")

workbook = openpyxl.load_workbook("D:\\marketing.xlsx")
worksheet = workbook['Лист1']

solver = SolverFactory('cbc', executable="D:\\cbc\\bin\\cbc.exe")

# Определение модели
model = ConcreteModel()

# Множество каналов интернет-трафика
model.I = RangeSet(1, 4)

# Параметры модели

model.budget = Param(initialize=worksheet['E2'].value)  # бюджет
model.C = Param(model.I,
                initialize={1: 0.068, 2: 0.135, 3: 0.135, 4: 0.059})  # стоимость одного клика для каждого канала
model.T = Param(model.I,
                initialize={1: 12, 2: 12, 3: 12, 4: 12})  # количество "покупаемых" по каждому каналу кликов
model.conversion = Param(initialize=0.03)  # 3% конверсия в лида
model.Lead_to_App = Param(model.I, initialize={1: 0, 2: 0.1, 3: 0.19, 4: 0})  # Конверися заявки в успешную сделку, %
model.App_to_Deal = Param(model.I,
                          initialize={1: 0.05, 2: 0.2, 3: 0.3, 4: 0.1})  # Конверися заявки в успешную сделку, %
model.Average_Check = Param(model.I, initialize={1: 610, 2: 170, 3: 351, 4: 771})  # средний чек для каждого канала
model.coverage = Param(model.I, initialize={1: 13503, 2: 10222, 3: 26983, 4: 11814})

# Определение переменных
model.x = Var(model.I, within=NonNegativeIntegers)


# Ограничения
def budget_constraint(model): #маркетинговый бюджеь
    print(sum(model.C[i] * model.T[i] * model.x[i] for i in model.I) <= model.budget)
    return sum(model.C[i] * model.T[i] * model.x[i] for i in model.I) <= model.budget


model.budget_con = Constraint(rule=budget_constraint)


def coverage_constraint(model, i): #по охвату каждого канала
    return model.T[i] * model.x[i] <= model.coverage[i] * sum(model.T[j] * model.x[j] for j in model.I)


model.clicks_con = Constraint(model.I, rule=coverage_constraint)


def obj_rule(model): #целевая функция
    revenue = sum(model.x[i] * model.conversion * model.Lead_to_App[i] * model.App_to_Deal[i] * model.Average_Check[i]
                  for i in model.I)
    return revenue


model.objective = Objective(rule=obj_rule, sense=maximize)



solver.solve(model)

print("Оптимальное решение:")
for i in model.I:
    print(f"x[{i}] = {model.x[i].value}")

print(f"Общий ожидаемый доход: {model.objective():.2f}")





# Определяем целевую функцию
def obj_rule(model):
    return sum(
        (model.RtU[t] + model.RtB[t] + model.RtI[t] + model.RtF[t]) * (1 - model.qpr) + model.RtD[t] for t in model.t)


model.obj = Objective(rule=obj_rule, sense=maximize)