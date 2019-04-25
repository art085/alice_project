from sympy import solve, sympify, symbols, simplify
from mpmath import *
import random
import sys
import re
import requests
from flask import Flask, request
import logging
import json

# словарь замен числительных
REPLACE_DIGITS = {
    'ноль':'0', 'один':'1', 'два':'2', 'три':'3', 'четыре':'4', 'пять':'5', 'шесть':'6', 'восемь':'8', 'семь':'7', 'девять':'9', 'десять':'10',
    'одиннадцать':'11', 'двенадцать':'12', 'тринадцать':'13', 'четырнадцать':'14', 'пятнадцать':'15', 'шестнадцать':'16',
    'семнадцать':'17', 'восемнадцать':'18', 'девятнадцать':'19',
    'двадцать':'20',
    'тридцать':'30',
    'сорок':'40',
    'пятьдесят':'50',
    'шестьдесят':'60',
    'семьдесят':'70',
    'восемьдесят':'80',
    'девяносто':'90',
    'сто':'100',
    'полтора':'1.5',
    'нуль':'0',
    'нулю':'0', 'одному':'1', 'двум':'2', 'трем':'3', 'четырем':'4', 'трём':'3', 'четырём':'4', 'пяти':'5', 'шести':'6', 'восьми':'8', 'семи':'7', 'девяти':'9', 'десяти':'10',
    'одного':'1', 'двух':'2', 'трех':'3', 'четырех':'4','трёх':'3', 'четырёх':'4',
    'биллион':'10**9',
    'триллион':'10**12',
    'квадриллион':'10**15',
    'квинтиллион':'10**18',
    'секстиллион':'10**21',
    'сиксилион':'10**21',
    'сиксиллион':'10**21',
    'септиллион':'10**24',
    'октиллион':'10**27',
    'нониллион':'10**30',
    'дециллион':'10**33',
    'х':'x', 'у':'y',
    'пи':'pi',
    'е':'E',
}
# словарь замен
REPLACE_ACTIONS = {
    'икс':'x', 'игрек':'y',
    'плюс':'+', 'минус':'-',
    'прибавить':'+',
    'отнять':'-',
    'помножить':'*',
    'умноженное':'*',
    'умножить':'*',
    '×':'*',
    '−':'-',
    '–':'-',
    'разделить':'/',
    'поделить':'/',
    'деленное':'/',
    'делить':'/',
    'дробь':'/',
    '÷':'/',
    ':':'/',
    ',':'.',
    'xy':'x*y',
    'yx':'y*x',
    'равняется':'=',
    'равно':'=',
    'равен':'=',
    'в квадрате':'**2',
    'квадрате':'**2',
    'в кубе':'**3',
    'кубе':'**3',
    'квадрат':'**2',
    'куб':'**3',
    'во второй':'**2',
    'в третьей':'**3',
    'в четвертой':'**4',
    'в пятой':'**5',
    'в шестой':'**6',
    'в седьмой':'**7',
    'в восьмой':'**8',
    'в девятой':'**9',
    'в десятой':'**10',
    'в степени':'**',
    ' факториал':'!',
    'число пи':'pi',
    'число е':'E',
    'число и':'I',
}
# словарь замен функций
REPLACE_FUNCTIONS = {
    'корень':'sqrt',
    'модуль':'abs',
    'косинус':'cos',
    'синус':'sin',
    'котангенс':'cot',
    'тангенс':'tan',
    'экспонента':'exp',
    'експонента':'exp',
    'логарифм':'log',
}
# варианты произношений скобок
REPLACE_BRACE = {
    'открывается':'открыть',
    'закрывается':'закрыть',
    'открываем':'открыть',
    'закрываем':'закрыть',
    'открылась':'открыть',
    'закрылась':'закрыть',
    'открылось':'открыть',
    'закрылось':'закрыть',
    'открылись':'открыть',
    'закрылись':'закрыть',
    'открылся':'открыть',
    'закрылся':'закрыть',
    'открыли':'открыть',
    'закрыли':'закрыть',
    'открыта':'открыть',
    'закрыта':'закрыть',
    'открыто':'открыть',
    'закрыто':'закрыть',
    'открыл':'открыть',
    'закрыл':'закрыть',
    'скобках':'скобка',
    'скобки':'скобка',
    'скобку':'скобка',
    'скобочка':'скобка',
    'скобочки':'скобка',
    'скобочку':'скобка',
    'скобу':'скобка',
    'открыть скобка':'(',
    'закрыть скобка':')',
    'скобка открыть':'(',
    'скобка закрыть':')',
    'левая скобка':'(',
    'правая скобка':')',
}
# словарь ошибок
ERRORS = {
    0:['Нет ошибок'],
    1:['Нет выражения','Необходимо ввести выражение', 'Укажите выражение'],
    2:['Уравнение должно содержать только одну переменную x или y', 'В вашем уравнении больше одной неизвестной'],
    3:['Уравнение может содержать только один знак равенства', 'В вашем уравнении несколько знаков равенства'],
    4:['В уравнении непарные скобки', 'Число отрывающихся скобок не равно числу закрывающихся'],
    5:['В выражении есть русские буквы. Попробуйте повторить', 'Выражение содержит русский текст. Попрбуйте перефразировать'],
}
# словарь озвучки результата
REPLACE_TTS = {
    'sqrt':' корень из ',
    '\*\*2':' в квадрате ',
    '\^2':' в квадрате ',
    '\*\*3':' в кубе ',
    '\^3':' в кубе ',
    '\*\*':' в степени ',
    '\^':' в степени ',
    '\*':' умножить на ',
    '-':' минус ',
    'acos':'арккосинус',
    'asin':'арксинус',
    'cos':'косинус',
    'sin':'синус',
    'cot':'котангенс',
    'tan':'тангенс',
    'log':'логарифм',
    'exp':'экспонента',
    'abs':'модуль',
    'LambertW':'W-функция Ламберта',
    'x':'икс',
    'y':'игрек',
    'pi':'пи',
    'E':'е',
    'I':'число и',
    '\(':' открыть скобку ',
    '\)':' закрыть скобку ',
    '\n':' - - ',
}
# словарь примеров
HELP_TEXTS = {
    'реши':['5x+12=7', 'cos(y)=sin(y)'],
    'вычисли':['5(76-6)', '2^5*sqrt(16)'],
    'упрости':['(2x-3y)(3y-2x)-12xy'],
}
# лишие слова, междометия
UNNECESSARY_WORDS = ['давай', 'на', 'ну', 'а', 'и', 'из', 'от']
# Команды решения
COMMAND_SOLV = ['реши', 'решить',  'решите', 'решение']
# Команды упрощения
COMMAND_SIMPL = ['упрости', 'упростить', 'упростите', 'ну прости', 'прости', 'опусти']
# Команды вычисления
COMMAND_CALC = ['вычисли', 'вычислить', 'сколько', 'найди']
# ответ на некорректный запрос
DEFAULT_ANSWER = ['У меня нет ответа.', 'Я просто решаю уравнения.', 'Этого я не понимаю.', 'Я не по этой части.', 'Я понимаю фразы начинающиеся словами: реши, вычисли, упрости.']
# точность (число знаков) для округления
CALC_PRECISION = 3
'''
Общие функции
'''
# Проверка строки на число
def is_digit(string):
    string = str(string)
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except (TypeError, ValueError):
            return False
# Классическое Округление (чтоб не было лишних нулей)
def rd(x):
    if not is_digit(x):
        return x
    if int(x) == x:
        return int(x)
    return x.round(CALC_PRECISION)

# Функция замены по словарю
def find_replace_multi(string, dictionary, use_word = False):
    for item in dictionary.keys():
        if use_word:
            string = re.sub(r'\b{}\b'.format(item), r'{}'.format(dictionary[item]), string)
        else:
            string = re.sub(item, dictionary[item], string)

    return str(string)

# Вставка математиченской функции в строку
def insert_function(fpattern, fname, string):
    start = string.find(fpattern)
    if start == -1:
        return string
    pat_len = len(fpattern)
    nam_len = len(fname)
    index1 = start + pat_len
    # делаем замену в зависимости от наличия скобки
    if '(' == re.search(r"\S", string[index1:]).group():
        string = string.replace(fpattern, fname, 1)
    else:
        string = string.replace(fpattern, fname+'(', 1)
        index2 = start + nam_len + 1
        # ищем позицию для закрытия скобки
        # первый непробельный и не знаки действий символ
        first = re.search(r"[^-+*/\s]", string[index2:]).start()
        index3 = index2 + first + 1
        # первый пробел после непробельного или конец строки
        space = re.search(r"\s", string[index3:])
        if space is None:
            end = len(string)
        else:
            end = index3 + space.start()
        string = string[:end] + ')' + string[end:]

    # если паттерн есть еще, повторяем
    if fpattern in string:
        string = insert_function(fpattern, fname, string)

    return string

'''
Основной класс обработки алгебраического выражения
'''
class Processing:
    def __init__(self, equation):
        # исходное выражение выбросим лишлие слова
        for item in UNNECESSARY_WORDS:
            equation = re.sub(r'\b{}\b'.format(item), '', equation)
        equation = equation.strip()
        # выделяем первое слово в команде
        parts = equation.split(' ', 1)
        self.first_word = parts[0]
        # исходное выражение
        self.equation = equation
        # код ошибки
        self.error = 0
        # тип задачи
        self.task = 'unknown'

    # Главный обработчик
    def process(self):
        self._prepare()
        if self.task == 'solve':
            self._solve()
        elif self.task == 'calculate':
            self._calculate()
        elif self.task == 'simplify':
            self._simplify()
        else:
            # дефолтный ответ на непонятный запрос
            self.answer = False

    # Предварительная подготовка выражения
    def _prepare(self):
        self.error = 0
        # Замена слов в тексте на переменные и цифры
        self.equation = find_replace_multi(self.equation, REPLACE_DIGITS, True)
        self.equation = find_replace_multi(self.equation, REPLACE_BRACE)
        self.equation = find_replace_multi(self.equation, REPLACE_ACTIONS)
        # ставим скобки если остались
        self.brace_placement()
        # убираем пробелы между числами
        self.equation = re.sub('(?<=\d)+ (?=\d)+', '', self.equation)
        # добавляем умножение
        # после чисел
        self.equation = re.sub(r'(\d+\)?)\s*([a-z(])' , r'\1*\2', self.equation)
        # перед скобкой
        self.equation = re.sub(r'([x,y])\s*\(', r'\1*(', self.equation)
        # между скобками
        self.equation = re.sub(r'\)\s*\(', r')*(', self.equation)
         # ставим функции, если есть
        for func in REPLACE_FUNCTIONS.keys():
            self.equation = insert_function(func, REPLACE_FUNCTIONS[func], self.equation)
        # добавляем умножение
        # после чисел
        self.equation = re.sub(r'(\d+\)?)\s*([a-z(])' , r'\1*\2', self.equation)
        # Заменяем i на I для корректной обработки мнимой единицы
        self.equation = re.sub(r"\bi\b","I" ,self.equation)
        # Заменяем e на E для корректной обработки числа e
        self.equation = re.sub(r"\be\b","E" ,self.equation)
        # базовые проверки
        # проверка соответствия скобок
        if not self.check_pairing():
            self.error = 4
        # проверка знаков равенства
        eqn = self.check_equality()
        if eqn > 1:
            self.error = 3
        # определяем тип задачи
        if any(c in self.equation for c in COMMAND_SOLV) or eqn == 1:
            self.task = 'solve'
        if any(c in self.equation for c in COMMAND_SIMPL):
            self.task = 'simplify'
        if any(c in self.equation for c in COMMAND_CALC):
            self.task = 'calculate'
        # если неясно и русского текста нет, смотрим по переменным
        if self.task == 'unknown' and not bool(re.search(r'[а-яА-ЯёЁ]', self.equation)):
            var_num = self.check_unknown()
            if var_num == 1:
                self.task = 'solve'
            elif var_num == 0:
                self.task = 'calculate'
            elif self.equation != '':
                self.task = 'simplify'
        # убираем оставшийся русский текст
        self.equation = re.sub('[а-яА-ЯёЁ]', '', self.equation)

    # Функция для решения уравнения
    def _solve(self):
        eqn = self.check_equality()
        # проверка числа перемнных
        var_num = self.check_unknown()
        # проверка на наличие выражения
        if self.equation == '':
            self.error = 1
        if var_num > 1:
            self.error = 2
        # сообщаем об ошибке
        if bool(self.error):
            self.answer = random.choice(ERRORS[self.error])
            return
        # если переменных нет, и нет равенства пытаемся вычислить
        if var_num == 0 and eqn == 0:
            self._calculate()
            return
        # переносим все в левую часть (приравниваем к 0)
        if eqn == 1:
            self.move()
        # пытаемся решить
        try:
            x, y = symbols('x,y')
            solution = solve(self.equation, dict=True)
        except NotImplementedError:
            self.answer = 'Такие уравнения я пока решать не умею'
        except Exception:
            self.answer = 'Ошибка в уравнении'
        else:
            if not solution:
                self.answer = 'Нет решений'
            else:
                res = []
                for sol in solution:
                    for key, value in sol.items():
                        # проверка если слишком длинный ответ, вычисляем
                        if len(str(value)) > 50:
                            ans = Processing(str(value))
                            ans._calculate()
                            res.append(str(key) + '=' + str(ans.answer))
                        else:
                            # Округляем
                            value = rd(value)
                            res.append(str(key) + '=' + str(value))
                self.answer = 'Ответ %s' % (' или '.join(res))

    # Функция вычисления выражения
    def _calculate(self):
        # проверка на наличие выражения
        if self.equation == '':
            self.error = 1
        # Проверка на ошибки
        if bool(self.error):
            self.answer = random.choice(ERRORS[self.error])
            return
        # проверка наличия равенства или переменной
        if self.check_equality() == 1 or self.check_unknown() == 1:
            self._solve()
        else:
            try:
                self.answer = sympify(self.equation).evalf(50)
                # Округляем
                self.answer = rd(self.answer)
            except Exception:
                self.answer = 'Ошибка в выражении'

    # Функция упрощения выражения
    def _simplify(self):
        # проверка на наличие выражения
        if self.equation == '':
            self.error = 1
        # Проверка на ошибки
        if bool(self.error):
            self.answer = random.choice(ERRORS[self.error])
            return
        # проверка равенства
        if self.check_equality() == 1:
            self._solve()
        else:
            try:
                self.answer = simplify(self.equation)
                # Округляем
                self.answer = rd(self.answer)
            except Exception:
                self.answer = 'Ошибка в выражении'

    # Расстановка скобок без вложенности
    def brace_placement(self, is_left=True):
        if 'скобка' in self.equation:
            brace = '(' if is_left else ')'
            self.equation = self.equation.replace('скобка', brace, 1).strip()
            self.brace_placement(not is_left)

    # перенос в одну часть (приравнивание к 0)
    def move(self):
        parts = self.equation.split('=')
        self.equation = parts[0].strip() + '-(' + parts[1].strip() + ')'
    # Определение числа вхождений равенства
    def check_equality(self):
        return self.equation.count("=")
    # Проверка парности скобок
    def check_pairing(self):
        return self.equation.count('(') == self.equation.count(')')
    # Проверка наличия неизвестной x или y
    def check_unknown(self):
        # проверка наличия x
        x_in = 'x' in self.equation
        # проверка наличия y
        y_in = 'y' in self.equation
        # сразу оба
        if x_in and y_in:
            return 2
        # нет ни x ни y
        if not (x_in or y_in):
            return 0
        # есть одна неизвестная
        return 1


app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

user_storage = {}

@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json, user_storage)
    logging.info('Request: %r', response)
    return json.dumps(response)

# Функция для непосредственной обработки диалога.
def handle_dialog(res, req, user_storage):
    user_id = req['session']['user_id']

    if req['session']['new'] or user_storage is None:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        user_storage = {
            'user_id': req['session']['user_id'],
            'suggests': [
            {'title': 'Помощь', 'hide': True},
            ],
            "to_log": True
        }

    # Флаг добавления в логи
    user_storage['to_log'] = True
    # данные о команде, убираем лишнее
    user_command = req['request']['command'].lower().replace('спроси знайка ответит', '').strip()
    # Подготавливаем класс обработчик
    process = Processing(user_command)
    # данные о исходном сообщении
    user_message = req['request']['original_utterance'].lower().strip()

    if not process.first_word:
        user_answer = 'Привет!\nЯ могу решать уравнения с одной неизвестной x или y,'+ \
        ' вычислять или упрощать выражения.\nПриступим? Если что, напиши "помощь".'
        res['response']['text'] = user_answer
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage

    # ответ яндекс боту
    if user_message == 'ping':
        res['response']['text'] = 'pong'
        user_storage['to_log'] = False
        return res, user_storage

    # ответ да
    if user_message == 'да' or user_message == 'давай':
        res['response']['text'] = 'Скажите слово: реши, вычисли или упрости и назовите выражение.'
        return res, user_storage
    # ответ нет
    if user_message == 'нет':
        res['response']['text'] = 'На нет и суда нет'
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage
    # Знакомство
    if user_message == 'как тебя зовут':
        res['response']['text'] = 'Меня зовут Порешала. И я люблю решать.'
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage

    # если похвалили
    if process.first_word in [
        'правильно',
        'офигеть',
        'молодец',
        'хорошо',
        'спасибо',
    ]:
        # Благодарим пользователя
        res['response']['text'] = 'Спасибо, я стараюсь!'
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage

    # всяко разное
    if process.first_word in [
        'привет',
        'ладно',
        'пожалуйста',
    ]:
        # отвечаем аналогично
        res['response']['text'] = 'Ну '+process.first_word
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage

    # помощь юзеру
    if process.first_word == 'помощь':
        res['response']['text'] = 'Я понимаю фразы начинающиеся с ключевых слов: ' + ', '.join(HELP_TEXTS) + \
        ', дополненные алгебраическим выражением.\n'+ \
        'Для примеров скажите: Пример и ключевое слово.\nЧтобы закончить скажите Выйти или Стоп.'
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage

    # примеры
    if process.first_word == 'пример':
        s = user_command.split(' ', 2)
        if len(s) == 1 or s[1] not in HELP_TEXTS:
            user_answer = "Укажите ключевое слово для примера: "+', '.join(HELP_TEXTS)
        else:
            user_answer = s[1]+' '+' или '.join(HELP_TEXTS[s[1]])

        res['response']['text'] = user_answer
        #res['response']['buttons'] = user_storage['suggests']
        return res, user_storage

    if process.first_word in [
        'выйти',
        'стоп',
        'хватит'
    ]:
        # Пользователь закончил, прощаемся.
        res['response']['text'] = 'Приходите ещё, порешаем!'
        res['response']['end_session'] = True
        return res, user_storage
    # Обрабатываем основные запросы
    process.process()

    # Если ошибка попробуем с исходным сообщением
    if isinstance(process.answer, str) and process.answer.startswith('Ошибка'):
        process = Processing(user_message)
        process.process()

    user_answer = str(process.answer if process.answer else random.choice(DEFAULT_ANSWER)+' Для подсказки скажите помощь.')

    res['response']['text'] = user_answer
    #res['response']['buttons'] = user_storage['suggests']

    return res, user_storage


if __name__ == '__main__':
    equation = ' '.join(sys.argv[1:])
    res = Processing(equation)
    res.process()
    if bool(res.error):
        res.answer = random.choice(ERRORS[res.error])
    user_answer = str(res.answer if res.answer else random.choice(DEFAULT_ANSWER))
    print(user_answer)
