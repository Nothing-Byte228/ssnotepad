import base64, hashlib, json, os, random, re, sys, urllib.parse
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, simpledialog

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.geometry("1000x700")
        self.filepath = sys.argv[1] if len(sys.argv) > 1 else None
        self.update_title()
        self.construct()
        if self.filepath: self.load_file(self.filepath)

    def update_title(self):
        self.root.title(f"SSNotepad — {os.path.basename(self.filepath) if self.filepath else 'Новый документ'}")

    def construct(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")
        
        self.text_area = tk.Text(self.main_frame, wrap="word", font=("Consolas", 11), undo=True, padx=10, pady=10, bd=0)
        self.text_area.pack(expand=True, fill="both")
        
        self.menubar = tk.Menu(self.root)
        
        # ФАЙЛ
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Новый файл", command=self.new_file)
        file_menu.add_command(label="Открыть...", command=self.open_file_dialog)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.destroy)
        self.menubar.add_cascade(label="Файл", menu=file_menu)
        
        # ГЛАВНОЕ МЕНЮ ИНСТРУМЕНТОВ
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        
        # Категории меню (10 штук по 10 фичей)
        cats = {
            "1. Регистр и Буквы (1-10)": [("1. Инвертировать регистр", self.f1), ("2. ВСЕ В ВЕРХНИЙ", self.f2), ("3. все в нижний", self.f3), ("4. Каждое Слово С Заглавной", self.f4), ("5. Предложение с заглавной.", self.f5), ("6. уБРАТЬ пЕРВУЮ бУКВУ сТРОКИ", self.f6), ("7. Сделать случайный регистр", self.f7), ("8. Транслитерация (Rus->Lat)", self.f8), ("9. Реверс букв в строках", self.f9), ("10. Удалить последнюю букву строк", self.f10)],
            "2. Очистка и Фильтры (11-20)": [("11. Удалить пустые строки", self.f11), ("12. Удалить дубликаты строк", self.f12), ("13. Удалить ВСЕ пробелы", self.f13), ("14. Схлопнуть лишние пробелы", self.f14), ("15. Удалить все цифры", self.f15), ("16. Удалить все спецсимволы", self.f16), ("17. Очистить HTML/XML теги", self.f17), ("18. Обрезать концевые пробелы", self.f18), ("19. Удалить строки содержащие...", self.f19), ("20. Удалить строки НЕ содержащие...", self.f20)],
            "3. Сортировка и Порядок (21-30)": [("21. Сортировать строки (А-Я)", self.f21), ("22. Сортировать строки (Я-А)", self.f22), ("23. Сортировать по длине строк", self.f23), ("24. Перемешать строки случайным образом", self.f24), ("25. Перевернуть порядок строк (Реверс)", self.f25), ("26. Сортировать по количеству слов", self.f26), ("27. Выровнять строки по левому краю", self.f27), ("28. Выровнять строки по правому краю", self.f28), ("29. Центрировать строки", self.f29), ("30. Сортировать числа в строках", self.f30)],
            "4. Трансформация строк (31-40)": [("31. Добавить нумерацию (1, 2...)", self.f31), ("32. Добавить римскую нумерацию", self.f32), ("33. Объединить всё в одну строку", self.f33), ("34. Разбить текст по точкам на строки", self.f34), ("35. Добавить префикс к строкам...", self.f35), ("36. Добавить суффикс к строкам...", self.f36), ("37. Заключить строки в кавычки", self.f37), ("38. Удалить кавычки в начале/конце строк", self.f38), ("39. Повторить каждую строку дважды", self.f39), ("40. Инвертировать порядок слов", self.f40)],
            "5. Криптография и Хэши (41-50)": [("41. Base64: Закодировать", self.f41), ("42. Base64: Декодировать", self.f42), ("43. Хэш: MD5", self.f43), ("44. Хэш: SHA-256", self.f44), ("45. Хэш: SHA-1", self.f44_1), ("46. Шифр Цезаря (Сдвиг +3)", self.f45), ("47. Расшифровать Цезаря (-3)", self.f46), ("48. Перевести в Двоичный код (Binary)", self.f47), ("49. Из Двоичного кода в текст", self.f48), ("50. Перевести в HEX", self.f49)],
            "6. Web, JSON и DEV (51-60)": [("51. Из HEX в текст", self.f50), ("52. JSON: Красивый формат (Pretify)", self.f51), ("53. JSON: Сжать в одну строку (Minify)", self.f52), ("54. URL Encode", self.f53), ("55. URL Decode", self.f54), ("56. Экранировать спецсимволы SQL", self.f55), ("57. Превратить текст в CSV (разделитель пробел)", self.f56), ("58. Извлечь все IPv4 адреса", self.f57), ("59. Превратить строки в JSON-массив строк", self.f58), ("60. Сгенерировать UUID/GUID", self.f60)],
            "7. Аналитика и Поиск (61-70)": [("61. Расширенная статистика", self.f61), ("62. Сумма чисел в тексте", self.f62), ("63. Найти самое длинное слово", self.f63), ("64. Найти самое короткое слово", self.f64), ("65. Посчитать вхождения слова...", self.f65), ("66. Проверить баланс скобок ()[]{}", self.f66), ("67. Извлечь все Email-адреса", self.f67), ("68. Извлечь все Веб-ссылки (URL)", self.f68), ("69. Показать частоту встречаемости букв", self.f69), ("70. Найти среднюю длину слова", self.f70)],
            "8. Генерация контента (71-80)": [("71. Вставить Дату и Время", self.f71), ("72. Вставить Lorem Ipsum", self.f72), ("73. Генератор паролей (16 знаков)", self.f73), ("74. Генератор PIN-кода (4 знака)", self.f74), ("75. Генератор случайных чисел (1-100)", self.f75), ("76. Сгенерировать никнейм", self.f76), ("77. Вставить текущий год", self.f77), ("78. Сгенерировать случайный цвет (HEX)", self.f78), ("79. Сгенерировать фейковый Email", self.f79), ("80. Сгенерировать фейковый телефон", self.f80)],
            "9. Текст по приколу (81-90)": [("81. Пробелы на ракеты 🚀", self.f81), ("82. Хакерский 1337 Speak", self.f82), ("83. Текст 'б л и н' Мод", self.f83), ("84. Оправдание для тимлида", self.f84), ("85. Вычислить выражение (Калькулятор)", self.f85), ("86. Заменить все гласные на '*'", self.f86), ("87. Добавить смайлик в конец строк", self.f87), ("88. Текст КРИКОМ (с восклицаниями)", self.f88), ("89. Текст шепотом (с троеточиями)", self.f89), ("90. Перемешать буквы в каждом слове", self.f90)],
            "10. Системные фичи (91-100)": [("91. Скопировать всё в буфер", self.f91), ("92. Очистить весь блокнот", self.f92), ("93. Посчитать разницу дней между 2 датами", self.f93), ("94. Сгенерировать SHA-512", self.f94), ("95. Заменить текст... (Find/Replace)", self.f95), ("96. Перевести текст в матерный Morse", self.f96), ("97. Вставить случайную цитату Конфуция", self.f97), ("98. Генератор броска кубика (d6/d20)", self.f98), ("99. Проверить текст на палиндром", self.f99), ("100. КНОПКА АБСОЛЮТНОГО СЧАСТЬЯ 🌟", self.f100)]
        }
        
        for cat_name, sub_items in cats.items():
            sub_menu = tk.Menu(tools_menu, tearoff=0)
            for lbl, cmd in sub_items: sub_menu.add_command(label=lbl, command=cmd)
            tools_menu.add_cascade(label=cat_name, menu=sub_menu)
            
        self.menubar.add_cascade(label="Инструменты", menu=tools_menu)
        
        # ВИД (4 ТЕМЫ ОФОРМЛЕНИЯ)
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="1. Тёмный Cyber (VS Code Style)", command=lambda: self.change_theme("cyber_dark"))
        view_menu.add_command(label="2. Классический светлый", command=lambda: self.change_theme("light"))
        view_menu.add_command(label="3. Матрица (Matrix Green) 🟢", command=lambda: self.change_theme("matrix"))
        view_menu.add_command(label="4. Киберпанк (Neon Synthwave) 🔮", command=lambda: self.change_theme("cyberpunk"))
        self.menubar.add_cascade(label="Вид", menu=view_menu)
        
        self.root.config(menu=self.menubar)
        self.change_theme("cyber_dark")

    # МИКРО-ХЕЛПЕРЫ ЯДРА
    def _g(self) -> str: return self.text_area.get("1.0", tk.END).rstrip("\n")
    def _s(self, t: str): self.text_area.delete("1.0", tk.END); self.text_area.insert("1.0", t)
    def _ins(self, t: str): self.text_area.insert(tk.INSERT, t)

    # РЕАЛИЗАЦИЯ 100 ФИЧЕЙ (ПЛОТНЫЙ ОПТИМИЗИРОВАННЫЙ КОД)
    def f1(self): self._s(self._g().swapcase())
    def f2(self): self._s(self._g().upper())
    def f3(self): self._s(self._g().lower())
    def f4(self): self._s(self._g().title())
    def f5(self): self._s("\n".join(s.capitalize() for s in self._g().splitlines()))
    def f6(self): self._s("\n".join(l[1:] if l else "" for l in self._g().splitlines()))
    def f7(self): self._s("".join(c.upper() if random.choice([True,False]) else c.lower() for c in self._g()))
    def f8(self):
        r,l="абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",["a","b","v","g","d","e","yo","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","kh","ts","ch","sh","shch","","y","","e","yu","ya","A","B","V","G","D","E","Yo","Zh","Z","I","Y","K","L","M","N","O","P","R","S","T","u","F","Kh","Ts","Ch","Sh","Shch","","Y","","E","Yu","Ya"]
        self._s("".join(dict(zip(r,l)).get(c,c) for c in self._g()))
    def f9(self): self._s("\n".join(l[::-1] for l in self._g().splitlines()))
    def f10(self): self._s("\n".join(l[:-1] if l else "" for l in self._g().splitlines()))
    def f11(self): self._s("\n".join(l for l in self._g().splitlines() if l.strip()))
    def f12(self):
        s=set(); self._s("\n".join(x for x in self._g().splitlines() if not (x in s or s.add(x))))
    def f13(self): self._s(self._g().replace(" ","").replace("\t",""))
    def f14(self): self._s(re.sub(r" +", " ", self._g()))
    def f15(self): self._s(re.sub(r"\d+", "", self._g()))
    def f16(self): self._s(re.sub(r"[^\w\sа-яА-ЯёЁ]", "", self._g()))
    def f17(self): self._s(re.sub(r"<[^>]*>", "", self._g()))
    def f18(self): self._s("\n".join(l.strip() for l in self._g().splitlines()))
    def f19(self):
        w=simpledialog.askstring("Фильтр", "Удалить строки с текстом:")
        if w: self._s("\n".join(l for l in self._g().splitlines() if w.lower() not in l.lower()))
    def f20(self):
        w=simpledialog.askstring("Фильтр", "Оставить только строки с текстом:")
        if w: self._s("\n".join(l for l in self._g().splitlines() if w.lower() in l.lower()))
    def f21(self): self._s("\n".join(sorted(self._g().splitlines())))
    def f22(self): self._s("\n".join(sorted(self._g().splitlines(), reverse=True)))
    def f23(self): self._s("\n".join(sorted(self._g().splitlines(), key=len)))
    def f24(self):
        l=self._g().splitlines(); random.shuffle(l); self._s("\n".join(l))
    def f25(self): self._s("\n".join(self._g().splitlines()[::-1]))
    def f26(self): self._s("\n".join(sorted(self._g().splitlines(), key=lambda x: len(x.split()))))
    def f27(self): self._s("\n".join(l.lstrip() for l in self._g().splitlines()))
    def f28(self): self._s("\n".join(l.rjust(80) for l in self._g().splitlines()))
    def f29(self): self._s("\n".join(l.center(80) for l in self._g().splitlines()))
    def f30(self): self._s("\n".join(" ".join(sorted(re.findall(r'\b\d+\b', l), key=int)) for l in self._g().splitlines()))
    def f31(self): self._s("\n".join(f"{i+1}. {l}" for i,l in enumerate(self._g().splitlines())))
    def f32(self):
        def r(n):
            val, sy = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1], ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
            i, rom = 0, ""
            while n > 0:
                for _ in range(n // val[i]): rom += sy[i]; n -= val[i]
                i += 1
            return rom
        self._s("\n".join(f"[{r(i+1)}] {l}" for i,l in enumerate(self._g().splitlines())))
    def f33(self): self._s(self._g().replace("\n", " "))
    def f34(self): self._s(self._g().replace(". ", ".\n").replace("? ", "?\n"))
    def f35(self):
        p=simpledialog.askstring("In","Префикс:"); self._s("\n".join(f"{p}{l}" for l in self._g().splitlines()) if p else self._g())
    def f36(self):
        p=simpledialog.askstring("In","Суффикс:"); self._s("\n".join(f"{l}{p}" for l in self._g().splitlines()) if p else self._g())
    def f37(self): self._s("\n".join(f'"{l}"' for l in self._g().splitlines()))
    def f38(self): self._s("\n".join(l.strip('"').strip("'") for l in self._g().splitlines()))
    def f39(self): self._s("\n".join(f"{l}\n{l}" for l in self._g().splitlines()))
    def f40(self): self._s("\n".join(" ".join(l.split()[::-1]) for l in self._g().splitlines()))
    def f41(self): self._s(base64.b64encode(self._g().encode("utf-8")).decode("utf-8"))
    def f42(self):
        try: self._s(base64.b64decode(self._g().encode("utf-8")).decode("utf-8"))
        except: messagebox.showerror("Err", "Bad Base64")
    def f43(self): messagebox.showinfo("MD5", hashlib.md5(self._g().encode()).hexdigest())
    def f44(self): messagebox.showinfo("SHA-256", hashlib.sha256(self._g().encode()).hexdigest())
    def f44_1(self): messagebox.showinfo("SHA-1", hashlib.sha1(self._g().encode()).hexdigest())
    def f45(self): self._s("".join(chr((ord(c) - 65 + 3) % 26 + 65) if c.isupper() else chr((ord(c) - 97 + 3) % 26 + 97) if c.islower() else c for c in self._g()))
    def f46(self): self._s("".join(chr((ord(c) - 65 - 3) % 26 + 65) if c.isupper() else chr((ord(c) - 97 - 3) % 26 + 97) if c.islower() else c for c in self._g()))
    def f47(self): self._s(" ".join(format(ord(c), "08b") for c in self._g()))
    def f48(self):
        try: self._s("".join(chr(int(b, 2)) for b in self._g().split()))
        except: messagebox.showerror("Err", "Bad Binary")
    def f49(self): self._s(self._g().encode("utf-8").hex())
    def f50(self):
        try: self._s(bytes.fromhex(self._g()).decode("utf-8"))
        except: messagebox.showerror("Err", "Bad HEX")
    def f51(self):
        try: self._s(json.dumps(json.loads(self._g()), indent=4, ensure_ascii=False))
        except: messagebox.showerror("Err", "Bad JSON")
    def f52(self):
        try: self._s(json.dumps(json.loads(self._g()), separators=(',', ':'), ensure_ascii=False))
        except: messagebox.showerror("Err", "Bad JSON")
    def f53(self): self._s(urllib.parse.quote(self._g()))
    def f54(self): self._s(urllib.parse.unquote(self._g()))
    def f55(self): self._s(self._g().replace("'", "''").replace('"', '""'))
    def f56(self): self._s("\n".join(",".join(l.split()) for l in self._g().splitlines()))
    def f57(self): self._s("\n".join(re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', self._g())))
    def f58(self): self._s(json.dumps(self._g().splitlines(), ensure_ascii=False))
    def f60(self): import uuid; self._ins(str(uuid.uuid4()))
    def f61(self):
        t=self._g(); messagebox.showinfo("Stat", f"Знаков: {len(t)}\nБез пробелов: {len(t.replace(' ',''))}\nСлов: {len(t.split())}\nСтрок: {len(t.splitlines())}")
    def f62(self): messagebox.showinfo("Sum", f"Сумма: {sum(map(int, re.findall(r'\b\d+\b', self._g())))}")
    def f63(self):
        w=re.findall(r"\b\w+\b", self._g()); messagebox.showinfo("Max", f"Длинное: {max(w,key=len) if w else 'No'}")
    def f64(self):
        w=re.findall(r"\b\w+\b", self._g()); messagebox.showinfo("Min", f"Короткое: {min(w,key=len) if w else 'No'}")
    def f65(self):
        w=simpledialog.askstring("Find","Слово:"); messagebox.showinfo("Res", f"Найдено: {self._g().lower().count(w.lower()) if w else 0}")
    def f66(self):
        s, b, d, ok = self._g(), [], {'(':')', '[':']', '{':'}'}, True
        for c in s:
            if c in d: b.append(c)
            elif c in d.values():
                if not b or d[b.pop()] != c: ok = False; break
        messagebox.showinfo("Скобки", "ОК" if ok and not b else "Ошибка!")
    def f67(self): self._s("\n".join(re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", self._g())))
    def f68(self): self._s("\n".join(re.findall(r"https?://[^\s<>\"']+", self._g())))
    def f69(self):
        from collections import Counter
        self._s("\n".join(f"'{k}': {v}" for k,v in Counter(self._g().lower()).most_common() if k.isalpha()))
    def f70(self):
        w=re.findall(r"\b\w+\b", self._g()); messagebox.showinfo("Avg", f"Средняя длина: {round(sum(len(x) for x in w)/len(w),2) if w else 0}")
    def f71(self): self._ins(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    def f72(self): self._ins("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin ac.")
    def f73(self): self._ins("".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*") for _ in range(16)))
    def f74(self): self._ins("".join(random.choice("0123456789") for _ in range(4)))
    def f75(self): self._ins(str(random.randint(1,100)))
    def f76(self): self._ins(random.choice(["Cyber","Hacker","Neo","Shadow","Giga","Zero"])+random.choice(["Player","Coder","Ghost","Sniper"]))
    def f77(self): self._ins(str(datetime.now().year))
    def f78(self): self._ins(f"#{random.randint(0, 0xFFFFFF):06x}")
    def f79(self): self._ins(f"user_{random.randint(100,999)}@fake-mail.com")
    def f80(self): self._ins(f"+7 (999) {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10,99)}")
    def f81(self): self._s(self._g().replace(" ", " 🚀 "))
    def f82(self):
        d={"а":"4","е":"3","и":"1","о":"0","с":"$","т":"7","a":"4","e":"3","o":"0","s":"5"}; self._s("".join(d.get(c.lower(),c) for c in self._g()))
    def f83(self): self._s(" блин ".join(self._g().split()))
    def f84(self): self._ins(f"\n[Отмазка]: {random.choice(['Локально работало.','Кэш не обновился.','Это вина легаси кода.','Конфликт версий.'])}\n")
    def f85(self):
        try: messagebox.showinfo("Res", f"Ответ: {eval(self._g(), {'__builtins__': None}, {})}")
        except: messagebox.showerror("Err", "Bad Expr")
    def f86(self): self._s(re.sub(r"[aeiouyаеёиоуыэюя]", "*", self._g(), flags=re.I))
    def f87(self): self._s("\n".join(f"{l} ツ" for l in self._g().splitlines()))
    def f88(self): self._s(" ".join(f"{w.upper()}!!!" for w in self._g().split()))
    def f89(self): self._s("... ".join(self._g().split()) + "...")
    def f90(self): self._s(" ".join("".join(random.sample(w, len(w))) for w in self._g().split()))
    def f91(self): self.root.clipboard_clear(); self.root.clipboard_append(self._g()); messagebox.showinfo("OK","Copied!")
    def f92(self): self._s("")
    def f93(self):
        try:
            d1, d2 = simpledialog.askstring("D1", "Дата 1 (ДД.ММ.ГГГГ):"), simpledialog.askstring("D2", "Дата 2 (ДД.ММ.ГГГГ):")
            t1, t2 = datetime.strptime(d1, "%d.%m.%Y"), datetime.strptime(d2, "%d.%m.%Y")
            messagebox.showinfo("Res", f"Разница: {abs((t1-t2).days)} дней")
        except: messagebox.showerror("Err", "Bad Date")
    def f94(self): messagebox.showinfo("SHA-512", hashlib.sha512(self._g().encode()).hexdigest())
    def f95(self):
        f, r = simpledialog.askstring("Find", "Что заменить:"), simpledialog.askstring("Replace", "На что:")
        if f is not None and r is not None: self._s(self._g().replace(f, r))
    def f96(self):
        d=dict(zip("abcdefghijklmnopqrstuvwxyz", [".-","-...","-.-.","-..",".", "code", "--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."]))
        self._s(" ".join(d.get(c.lower(), "?") for c in self._g() if c.isalpha() or c==" "))
    def f97(self): self._ins(f"\n[Конфуций]: {random.choice(['Драгоценный камень нельзя отполировать без трения.','Посылая стрелу истины, мочи её кончик в мёде.','Остерегайтесь того, кто обещает всё за ничего.'])}\n")
    def f98(self): messagebox.showinfo("Dice", f"d6: {random.randint(1,6)} | d20: {random.randint(1,20)}")
    def f99(self):
        c=re.sub(r'[^\w]', '', self._g().lower()); messagebox.showinfo("Res", "Палиндром!" if c==c[::-1] else "Нет")
    def f100(self): messagebox.showinfo("🌟","Всё просто великолепно! Ты лучший кодер 2026 года!")

    # КРУТЫЕ ТЕМЫ ОФОРМЛЕНИЯ
    def change_theme(self, theme):
        themes = {
            "cyber_dark": {"bg": "#1e1e1e", "fg": "#d4d4d4", "cur": "#007acc"},
            "light": {"bg": "#ffffff", "fg": "#000000", "cur": "black"},
            "matrix": {"bg": "#000000", "fg": "#00ff00", "cur": "#00ff00"},
            "cyberpunk": {"bg": "#2b003a", "fg": "#00ffcc", "cur": "#ff007f"}
        }
        cfg = themes.get(theme, themes["cyber_dark"])
        self.root.config(bg=cfg["bg"])
        self.main_frame.config(bg=cfg["bg"])
        self.text_area.config(bg=cfg["bg"], fg=cfg["fg"], insertbackground=cfg["cur"])
        self.menubar.config(bg=cfg["bg"], fg=cfg["fg"])

    # СТАНДАРТНЫЙ МЕНЕДЖМЕНТ ФАЙЛОВ
    def new_file(self): self.text_area.delete("1.0", tk.END); self.filepath = None; self.update_title()
    def open_file_dialog(self):
        f = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Текст", "*.txt")])
        if f: self.load_file(f)
    def load_file(self, path):
        with open(path, "r", encoding="utf-8") as f: self._s(f.read())
        self.filepath = path; self.update_title()
    def save_file(self):
        if not self.filepath: self.filepath = filedialog.asksaveasfilename(defaultextension=".txt")
        if self.filepath:
            with open(self.filepath, "w", encoding="utf-8") as f: f.write(self._g())
            self.update_title()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()