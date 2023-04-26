import random
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
import math

INPUT_FUNS = ["(x - 2)**4 + (x - 2*y)**2"]


# ------------------------------------algorithm-realisation-------------------------------------------------------------
def func(x, y):
    return eval(INPUT_FUNS[0])  # (x - 2)**4 + (x - 2*y)**2


def generate_initial_population(size, start, end):
    population = []
    for i in range(size):
        x = random.uniform(start, end)
        y = random.uniform(start, end)
        v = [random.uniform(-5, 5), random.uniform(-5, 5)]
        it = [x, y, v, func(x, y)]
        population.append(it)
    return population


def swarm_algorithm(num_generations, population_size, start, end, fi_p, fi_g, k):
    """
    :param num_generations: критерий останова - кол-во итераций алгоритма
    :param population_size: размер исходной популяции
    :param start: нижняя граница поиска
    :param end: верхняя граница поиска
    :param fi_p + fi_g: > 4
    :param k: в интервале (0, 1)
    """
    stop_ind = -1

    dataForTable = []
    snapshot_arr = []

    r_p = random.random()
    r_g = random.random()
    fi = fi_p + fi_g
    K = 2 * k / (abs(2 - fi - math.sqrt(pow(fi, 2) - 4 * fi)))

    # генерируем исходную популяцию
    now_population = generate_initial_population(population_size, start, end)
    best_population = now_population
    best_val = sorted(best_population, key=lambda z: z[3])[0]

    for i in range(num_generations):
        for _ in range(population_size):
            # корректируем скорость для кажой частицы
            new_v_x = K * (best_population[_][2][0] + fi_p * r_p *
                           (best_population[_][0] - now_population[_][0]) +
                           fi_g * r_g * (best_val[0] - now_population[_][0]))
            new_v_y = K * (best_population[_][2][1] + fi_p * r_p *
                           (best_population[_][1] - now_population[_][1]) +
                           fi_g * r_g * (best_val[1] - now_population[_][1]))
            new_v = [new_v_x, new_v_y]
            now_population[_][2] = new_v

            # корректируем координаты каждой частицы
            now_population[_][0] += new_v_x
            now_population[_][1] += new_v_y
            now_population[_][3] = func(now_population[_][0], now_population[_][1])

            # ищем лучшее решение для каждой частицы
            if now_population[_][3] < best_population[_][3]:
                best_population[_] = now_population[_]

        # проверяем не нашли ли глобальную лучшую точку
        best_val = sorted(best_population, key=lambda z: z[3])[0]

        # записываем данные для изуализации таблицы
        dataForTable.append([best_val[0], best_val[1], best_val[3]])

        # Отрисовка и сохранение графика

        x_best = list(map(lambda x: x[0], best_population))
        y_best = list(map(lambda x: x[1], best_population))
        snapshot_name = f"pictures/g{i}.png"
        fig, ax2 = plt.subplots(1, 1)
        fig.suptitle(f"Номер поколения: {i + 1}")
        ax2.set_xlabel("Лучшие решения на всех итерациях")
        ax2.plot(x_best, y_best, 'go')
        ax2.set_xlim(start, end)
        ax2.set_ylim(start, end)
        plt.savefig(snapshot_name, dpi=70, bbox_inches='tight')
        plt.close()
        snapshot_arr.append(snapshot_name)

        if i > 3:
            if round(dataForTable[i][1], 3) == round(dataForTable[i - 1][1], 3) == \
                    round(dataForTable[i - 2][1], 3) and \
                    round(dataForTable[i][0], 3) == round(dataForTable[i - 1][0], 3) == \
                    round(dataForTable[i - 2][0], 3):
                stop_ind = i
                break

    # Сохраняем таблицу
    data = pd.DataFrame(dataForTable)
    data.columns = ['X', 'Y', 'Наименьшее значение F(x,y)']

    print("Минимум функции в точке(", best_val[0], best_val[1], "), значение функции: ",
          best_val[3])

    return best_val, data, stop_ind


# -------------------------------img-and-table-frames-logic--------------------------------------------------------------
class ShowResult:
    def __init__(self, data, stop_ind):
        # Счётчик для изображений
        self.i = 0
        if stop_ind == -1:
            self.max_i = int(num_generations.item.get()) - 1
        else:
            self.max_i = stop_ind
            # Рамка для наших изображений
        self.canvas = Canvas(frame_btn, width=420, height=345, borderwidth=2)

        # Добавим 1-ое изображение
        self.photo = None
        self.show_img()

        # Кнопки для перелистывания изображений
        self.button_next = ttk.Button(frame_btn, text="Далее", command=self.next_img, state=NORMAL)
        self.button_next.grid(row=1, column=1)
        self.button_back = ttk.Button(frame_btn, text="Назад", command=self.previous_img, state=DISABLED)
        self.button_back.grid(row=1, column=0)

        # Выведем таблицу
        self.data = data
        self.show_table()

    def next_img(self) -> None:
        self.i += 1
        self.button_back['state'] = NORMAL
        self.show_img()
        if self.i == self.max_i:
            self.button_next['state'] = DISABLED

    def previous_img(self) -> None:
        self.i -= 1
        self.button_next['state'] = NORMAL
        self.show_img()
        if self.i == 0:
            self.button_back['state'] = DISABLED

    def show_img(self):
        self.photo = ImageTk.PhotoImage(Image.open("pictures/g{0}.png".format(self.i)))
        self.canvas.create_image(3, 3, anchor='nw', image=self.photo)
        self.canvas.grid(column=0, row=0, columnspan=2)

    def show_table(self) -> None:
        # Создаем виджет таблицы
        treeview = ttk.Treeview(frame_scroll, columns=list(self.data.columns), show='headings')
        treeview.pack(side=LEFT, fill=BOTH, expand=1)
        # Добавляем колонки в таблицу
        for col in self.data.columns:
            treeview.heading(col, text=col)
        # Добавляем строки в таблицу и заполняем значения ячеек данными из дата-фрейма
        for i, row in self.data.iterrows():
            treeview.insert('', END, values=list(row))
        # Создаем scrollbar widget и добавляем его в таблицу
        scrollbar = ttk.Scrollbar(frame_scroll, orient=VERTICAL, command=treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        treeview.configure(yscrollcommand=scrollbar.set)


# ------------------------------------------------buttons-logic----------------------------------------------------------

def checkButtonState(*args) -> None:
    """ Кнопка активируется когда все атрибуты input введены """
    if num_generations.item.get() and population_size.item.get() and \
            start.item.get() and end.item.get() and combobox:
        btn_start['state'] = NORMAL
    else:
        btn_start['state'] = DISABLED
    if num_generations.item.get() or population_size.item.get() or \
            start.item.get() or end.item.get() or combobox:
        btn_clean['state'] = NORMAL


def clickButton() -> None:
    """ По нажатию кнопки производятся расчёты """
    btn_start['state'] = DISABLED
    xy_bestScore, data, stop_ind = \
        swarm_algorithm(population_size=int(population_size.item.get()),
                        num_generations=int(num_generations.item.get()),
                        start=min(int(start.item.get()), int(end.item.get())),
                        end=max(int(start.item.get()), int(end.item.get())),
                        fi_p=float(fi_p.item.get()),
                        fi_g=float(fi_g.item.get()),
                        k=float(k.item.get()))

    # Перед тем как сгенерировать новые виджеты, удалим старые
    for widget in frame_input.winfo_children():
        if widget.winfo_name() == "result_label":
            widget.destroy()
    for widget in frame_btn.winfo_children():
        widget.destroy()
    for widget in frame_scroll.winfo_children():
        widget.destroy()

    # Создаём новые
    ShowResult(data, stop_ind)
    text = "x={0} y={1}; \n Наименьшее значение F(x,y): {2}".format(xy_bestScore[0],
                                                                    xy_bestScore[1],
                                                                    xy_bestScore[3])
    Label(frame_input, text=text, fg='green', font=('Arial', 10), name="result_label").pack()


def cleanButton() -> None:
    """ По нажатию кнопки удаляем старые данные """
    population_size.item.delete(0, END)
    num_generations.item.delete(0, END)
    start.item.delete(0, END)
    end.item.delete(0, END)
    combobox.set('')
    for widget in frame_input.winfo_children():
        if widget.winfo_name() == "result_label":
            widget.destroy()
    for widget in frame_btn.winfo_children():
        widget.destroy()
    for widget in frame_scroll.winfo_children():
        widget.destroy()


# ---------------------------------------user-input----------------------------------------------------------------------

class UserInput:
    """ Класс определяющий шаблон для атрибутов ввода tkinter """

    def __init__(self, text, from_, to, increment, initial_value):
        # Текстовые переменные tkinter
        self.var = StringVar()  # текст вводимый пользователем
        self.var.set(initial_value)

        # Определяем структуру объекта ввода
        Label(frame_input, text=text).pack()
        self.item = ttk.Spinbox(frame_input, validate='key', textvariable=self.var,
                                from_=from_, to=to, increment=increment)
        self.item.pack()
        self.var.trace('w', checkButtonState)


# -------------------------------------------------UI--------------------------------------------------------------------

# Создаётся окно пользователя
root_window = Tk()
root_window.title("PRACTICLE SWARM ALGORITHM")
root_window.geometry('1000x660')

# Создание фреймов и настройка их свойств
frame_input = Frame(root_window, bd=3, relief=GROOVE)
Label(frame_input, text="АЛГОРИТМ РОЯ ЧАСТИЦ", font=('Arial', 16)).pack(pady=10)
frame_input.grid(column=0, row=0, rowspan=2, sticky='NSEW')

frame_img = LabelFrame(root_window, bd=3, relief=GROOVE, text="Графики")
frame_img.grid(column=1, row=0, sticky='NSEW')
frame_table = LabelFrame(root_window, bd=3, relief=GROOVE, text="Таблица")
frame_table.grid(column=1, row=1, sticky='NSEW')

# Дополнительные мини-фреймы
frame_btn = Frame(frame_img)
frame_btn.pack(fill=BOTH, expand=1)
frame_scroll = Frame(frame_table)
frame_scroll.pack(fill=BOTH, expand=1)

# Задание параметров для столбцов и строк
root_window.columnconfigure(0, weight=1)
root_window.columnconfigure(1, weight=4)
root_window.rowconfigure(0, weight=1)
root_window.rowconfigure(1, weight=1)

# Ввод функции которую мы хотим исследовать
Label(frame_input, text="Целевая функция:").pack()
var_txt = StringVar()
combobox = ttk.Combobox(frame_input, textvariable=var_txt)
combobox['values'] = INPUT_FUNS
combobox['state'] = 'readonly'
combobox.pack(padx=5, pady=5)
var_txt.trace('w', checkButtonState)

# Ввод данных
population_size = UserInput(text="Размер популяции первого поколения:", initial_value="10", from_=2, to=999,
                            increment=1)
num_generations = UserInput(text="Количество поколений:", initial_value="10", from_=1, to=999, increment=1)
start = UserInput(text="Нижняя граница диапазона поиска:", initial_value="-5", from_=-99999, to=99999, increment=1)
end = UserInput(text="Верхняя граница диапазона поиска:", initial_value="5", from_=-99999, to=99999, increment=1)

Label(frame_input, text="", font=('Arial', 10)).pack()
Label(frame_input, text="Коэффициенты при коррекции скорости частиц:", font=('Arial', 10)).pack()
Label(frame_input, text="", font=('Arial', 1)).pack()
Label(frame_input, text="Введите коэффициенты так, чтобы φp + φg > 4 и k∈(0, 1):", font=('Arial', 8)).pack()
fi_p = UserInput(text="φp: весовой коэффициент при координатах лучшего решения текущей частицы:", initial_value="5.0",
                 from_=-99999.0, to=99999.0, increment=1.0)
fi_g = UserInput(text="φg: весовой коэффициент при координатах лучшего решения всех частиц:", initial_value="5.0",
                 from_=-99999.0, to=99999.0, increment=1.0)
k = UserInput(text="k: коэффициент нормировки φp, φg:", from_=0.001, to=0.999, increment=0.01, initial_value="0.5")

# Запуск программы
btn_start = ttk.Button(frame_input, text="Рассчитать", command=clickButton, state=DISABLED)
btn_start.pack(padx=5, pady=5)

# Очистить старые значения
btn_clean = ttk.Button(frame_input, text="Очистить", command=cleanButton, state=DISABLED)
btn_clean.pack(padx=5, pady=5)

root_window.mainloop()
