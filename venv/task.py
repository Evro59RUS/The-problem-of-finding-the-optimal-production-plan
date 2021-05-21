#Задачка:
#Есть предприятие, которое производит питццу и пирожки с начинкой.
# У каждой категории продуктов есть свое кол-во ингредиентов. Нужно написать программу, которая по остаткам на складе вычислит:
#- каких изделий можно произвести больше?
#- каких изделий нужно произвести, что бы получить максимальную выгоду
# (в спецификации есть отпускная цена, в остатках склада - закупочная цена)?

#Информацию можно хранить в файле или в базе.

#mp !!!.pdf на рабочем столе

import sqlite3
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable

class product:
    def __init__(self,id, n, ingr, p):
        self.product_ID = id
        self.name = n
        self.ingridients = ingr
        self.selling_price = p
        self.validity = 0

class ingridient:
    def __init__(self,id, n, p, b):
        self.ingridient_ID = id
        self.name = n
        self.cost_price = p
        self.balance = b


def DbReadData(Ingridients,Sklad,Products):
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    cur1 = con.cursor()
    cur.execute('select ingridient_ID, name, cost_price, balance from ingridient')
    IngridientLines = cur.fetchall()

    for a in IngridientLines:
        Ingridients.append(ingridient(a[0],a[1],a[2],a[3]))
        Sklad.append(a[3])

    #перепилим потом чтобы коллекция ингридиентов была
    cur.execute('select product_ID, name, selling_price from product')
    ProductLines = cur.fetchall()

    i = 1
    while (i <= len(ProductLines)):
        cur1.execute('select ID_of_ingridient, quantity from ingridients_for_products where ID_of_product=?',(ProductLines[i-1][0],))
        mas = cur1.fetchall()
        Products.append(product(ProductLines[i-1][0],ProductLines[i-1][1],mas,ProductLines[i-1][2]))
        i+=1
    cur.close()
    con.close()

def MaximumOfEachProducts(Ingridients,Sklad,Products):
    i=1
    while (i <= len(Products)):#идём по всем продуктам и по всем ингридиентам для этих продуктов и ищем наименьшее частное остатков на складе данного продукта и количества уе этого продукта для изготовления единицы товара.
        j=1
        mincount = 10000000000000000000
        while (j <= len(Products[i-1].ingridients)):
            ID_of_ingridient = Products[i - 1].ingridients[j-1][0]
            quantity = Products[i - 1].ingridients[j-1][1]
            if (mincount > Sklad[ID_of_ingridient-1] // quantity):
                mincount = Sklad[ID_of_ingridient - 1] // quantity
            j+=1
        print("максимальное количество " + str(Products[i-1].name)+ " которое можно произвести из остатков на складе составляет " + str(mincount) +" единиц")
        i+=1;

def FindIngridientInProduct(Products, numberofproduct, numberofingridient):
    for i in range (0,len(Products[numberofproduct].ingridients)):
        if (Products[numberofproduct].ingridients[i][0]==numberofingridient+1):
            return Products[numberofproduct].ingridients[i][1]
    return 0

def CalcRestriction(numberofingridient, Products ,Sklad, variables):#функция возвращающая выражение типа am1*x1+am2*x2+...+amn*xn<=Am
    summa = 0
    for i in range (0, len(variables)):
        summa += variables[i] * FindIngridientInProduct(Products,i,numberofingridient)
    return (summa <= Sklad[numberofingridient])

def SelfValidity(product,Ingridients):#функция считает прибыльность продукта
    cost = 0
    for i in range (0,len(product.ingridients)):
        cost += product.ingridients[i][1] * Ingridients[product.ingridients[i][0]-1].cost_price
    product.validity = product.selling_price - cost

def MaxFunc(variables,Products):#собираем функцию которую будем максимизировать
    maxfunc=0
    for i in range (0,len(Products)):
        maxfunc += Products[i].validity * variables[i]

    return maxfunc

def main():
    #main
    Ingridients = []
    Sklad = []
    Products = []

    DbReadData(Ingridients,Sklad,Products)#читаем данные из базы
    for i in Products:#посчитаем прибыль от изготовления единицы товара
        SelfValidity(i,Ingridients)


    #решаем задачу максимизации прибыли симплекс методом
    #Модель: Задача нахождения оптимального плана выпуска продукции
    #https://www.hse.ru/mirror/pubs/share/183952798
    #пример взят отсюда
    #https://docplayer.ru/28035351-Laboratornaya-rabota-1-zadacha-raspredeleniya-neodnorodnyh-resursov-sostavlenie-optimalnogo-plana-vypuska-produkcii.html
    model = LpProblem(name="small-problem", sense=LpMaximize)

    variables = []#переменные модели // продукты
    for product in Products:
        variables.append(LpVariable(name=product.name, lowBound = 0, cat="Integer"))
    # Добавляем ограничения

    for i in range(0 , len(Ingridients)):
        model += (CalcRestriction(i,Products,Sklad,variables),Ingridients[i].name)#выражение типа am1*x1+am2*x2+...+amn*xn<=Am

    # Добавляем целевую функцию
    # Вариант добавления через lpSum
    a = MaxFunc(variables,Products)
    model += lpSum(a)

    # Решаем задачу оптимизации
    status = model.solve()

    #ответы
    print(f"status: {model.status}, {LpStatus[model.status]}")

    print(f"objective: {model.objective.value()}")

    for var in model.variables():
        print(f"{var.name}: {var.value()}")

    MaximumOfEachProducts(Ingridients,Sklad,Products)#смотрим сколько единиц каждого товара можно произвести


main()