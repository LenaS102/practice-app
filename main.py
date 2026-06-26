# ============================================================
# ОБРАБОТКА ИЗОБРАЖЕНИЙ - ВАРИАНТ 20
# Студент: Соколова Е.А.
# Группа: ЗКИ25-18Б
# ============================================================

import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog


class ImageProcessorApp:
    """
    Приложение для обработки изображений.

    Реализует базовый функционал (загрузка, камера, цветовые каналы)
    и функции варианта №20 (обрезка, яркость, рисование зелёной линии).
    """

    # ============================================================
    # КОНСТАНТЫ
    # ============================================================

    # Размеры окон (все хранятся как строки "ширина x высота")
    MAIN_WINDOW_SIZE = "900x650"
    CAMERA_WINDOW_SIZE = "640x550"
    CHANNEL_WINDOW_SIZE = "800x500"
    CROP_DIALOG_SIZE = "300x280"
    LINE_DIALOG_SIZE = "300x330"

    # Ограничения для отображения изображения
    MAX_DISPLAY_WIDTH = 700
    MAX_DISPLAY_HEIGHT = 450

    # Размеры кнопок
    BUTTON_WIDTH = 22
    BUTTON_HEIGHT = 2

    # Шрифты
    STATUS_FONT = ("Arial", 10)
    TITLE_FONT = ("Arial", 18, "bold")
    LABEL_FONT = ("Arial", 14)

    # ============================================================
    # ИНИЦИАЛИЗАЦИЯ
    # ============================================================

    def __init__(self, root):
        """
        Инициализирует главное окно приложения.

        Создаёт графический интерфейс, настраивает переменные
        для хранения изображений и подготавливает состояние камеры.
        """
        self.root = root
        self.root.title("Обработка изображений - Вариант 20")
        self.root.geometry(self.MAIN_WINDOW_SIZE)
        self.root.configure(bg="#ffffff")

        self.original_image = None
        self.processed_image = None
        self.cap = None
        self.is_camera_on = False

        self._setup_ui()

    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ (приватные)
    # ============================================================

    def _setup_ui(self):
        """Создаёт все элементы графического интерфейса."""
        # Заголовок программы
        title = tk.Label(
            self.root,
            text="Обработка изображений",
            font=self.TITLE_FONT,
            bg="#ffffff"
        )
        title.pack(pady=15)

        # Рамка для кнопок
        button_frame = tk.Frame(self.root, bg="#ffffff")
        button_frame.pack(pady=10)

        # ======== РЯД 1. БАЗОВЫЙ ФУНКЦИОНАЛ ========

        btn_load = tk.Button(
            button_frame,
            text="Загрузить изображение",
            command=self.load_image,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_load.grid(row=0, column=0, padx=5, pady=3)

        btn_camera = tk.Button(
            button_frame,
            text="Снять с камеры",
            command=self.camera_window,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_camera.grid(row=0, column=1, padx=5, pady=3)

        btn_channels = tk.Button(
            button_frame,
            text="Цветовые каналы",
            command=self.show_channels,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_channels.grid(row=0, column=2, padx=5, pady=3)

        # ======== РЯД 2. ФУНКЦИИ ВАРИАНТА 20 ========

        btn_crop = tk.Button(
            button_frame,
            text="Обрезка",
            command=self.crop_image,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_crop.grid(row=1, column=0, padx=5, pady=3)

        btn_brightness = tk.Button(
            button_frame,
            text="Яркость",
            command=self.adjust_brightness,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_brightness.grid(row=1, column=1, padx=5, pady=3)

        btn_line = tk.Button(
            button_frame,
            text="Зелёная линия",
            command=self.draw_line,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_line.grid(row=1, column=2, padx=5, pady=3)

        btn_reset = tk.Button(
            button_frame,
            text="Сброс",
            command=self.reset_image,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_reset.grid(row=1, column=3, padx=5, pady=3)

        # ======== ОБЛАСТЬ ДЛЯ ОТОБРАЖЕНИЯ ИЗОБРАЖЕНИЯ ========

        self.image_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.image_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(
            self.image_frame,
            text="Загрузите изображение",
            font=self.LABEL_FONT,
            bg="#f0f0f0"
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # ======== СТРОКА СОСТОЯНИЯ ========

        self.status_label = tk.Label(
            self.root,
            text="Готов",
            font=self.STATUS_FONT,
            bg="#ffffff",
            fg="#333333"
        )
        self.status_label.pack(pady=5)

        info = tk.Label(
            self.root,
            text="Вариант 20: обрезка, яркость, зелёная линия",
            font=self.STATUS_FONT,
            fg="#666666",
            bg="#ffffff"
        )
        info.pack(pady=5)

    def _display_image(self, image):
        """
        Показывает изображение в центре окна.

        Автоматически подгоняет размер под окно.
        """
        if image is None:
            return

        # OpenCV хранит цвета в порядке BGR, а Tkinter ожидает RGB
        if len(image.shape) == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image

        # Определяем размеры изображения
        if len(rgb_image.shape) > 2:
            height, width = rgb_image.shape[:2]
        else:
            height, width = rgb_image.shape[0], rgb_image.shape[1]

        # Ограничиваем размер
        scale = min(
            self.MAX_DISPLAY_WIDTH / width,
            self.MAX_DISPLAY_HEIGHT / height,
            1
        )
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Изменяем размер изображения
        if len(rgb_image.shape) == 3:
            resized = cv2.resize(rgb_image, (new_width, new_height))
        else:
            resized = cv2.resize(rgb_image, (new_width, new_height))

        # Конвертируем в формат Tkinter
        pil_image = Image.fromarray(resized)
        imgtk = ImageTk.PhotoImage(image=pil_image)

        self.image_label.config(image=imgtk, text="")
        self.image_label.image = imgtk

    def _update_video(self, label, window):
        """Обновляет видео с камеры в реальном времени."""
        if not self.is_camera_on or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=pil)
            label.config(image=imgtk)
            label.image = imgtk

        if self.is_camera_on:
            self.root.after(30, lambda: self._update_video(label, window))

    def _display_channel_in_window(self, image, channel_name):
        """Отображает изображение с одним каналом в отдельном окне."""
        channel_win = tk.Toplevel(self.root)
        channel_win.title(channel_name + " канал")
        channel_win.geometry(self.CHANNEL_WINDOW_SIZE)
        channel_win.configure(bg="#ffffff")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        height, width = rgb.shape[:2]
        max_size = 450
        scale = min(max_size / width, max_size / height, 1)
        new_width, new_height = int(width * scale), int(height * scale)
        pil = pil.resize((new_width, new_height))

        imgtk = ImageTk.PhotoImage(pil)
        label = tk.Label(channel_win, image=imgtk, bg="#ffffff")
        label.image = imgtk
        label.pack(pady=20)

        tk.Label(
            channel_win,
            text=channel_name + " канал",
            font=self.LABEL_FONT,
            bg="#ffffff"
        ).pack()

    def _validate_image_loaded(self):
        """Проверяет, загружено ли изображение."""
        if self.processed_image is None:
            messagebox.showerror("Ошибка", "Сначала загрузите изображение")
            return False
        return True

    def _show_error(self, message):
        """Показывает сообщение об ошибке."""
        messagebox.showerror("Ошибка", message)

    # ============================================================
    # ПУБЛИЧНЫЕ МЕТОДЫ (для кнопок)
    # ============================================================

    def load_image(self):
        """Загружает изображение из файла."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg")]
        )

        if not file_path:
            return

        try:
            self.original_image = cv2.imdecode(
                np.fromfile(file_path, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )

            if self.original_image is None:
                raise ValueError("Не удалось прочитать файл")

            self.processed_image = self.original_image.copy()
            self._display_image(self.processed_image)

            file_name = file_path.split("/")[-1]
            self.status_label.config(text="Загружено: " + file_name)

        except Exception as error:
            self._show_error(str(error))

    def camera_window(self):
        """Открывает окно для работы с веб-камерой."""
        cam_win = tk.Toplevel(self.root)
        cam_win.title("Веб-камера")
        cam_win.geometry(self.CAMERA_WINDOW_SIZE)
        cam_win.configure(bg="#ffffff")

        video_label = tk.Label(cam_win, bg="#000000")
        video_label.pack(pady=10)

        btn_frame = tk.Frame(cam_win, bg="#ffffff")
        btn_frame.pack(pady=10)

        def start_camera():
            """Запускает камеру."""
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise RuntimeError("Камера не обнаружена")
                self.is_camera_on = True
                self._update_video(video_label, cam_win)
                self.status_label.config(text="Камера запущена")
            except Exception as error:
                self._show_error(str(error))

        def capture_photo():
            """Делает снимок с камеры."""
            if self.cap is None or not self.is_camera_on:
                self._show_error("Сначала запустите камеру")
                return

            ret, frame = self.cap.read()
            if ret:
                self.original_image = frame.copy()
                self.processed_image = frame.copy()
                self._display_image(self.processed_image)
                self.status_label.config(text="Снимок сделан")
                cam_win.destroy()
            else:
                self._show_error("Не удалось сделать снимок")

        def stop_camera():
            """Останавливает камеру и закрывает окно."""
            self.is_camera_on = False
            if self.cap:
                self.cap.release()
                self.cap = None
            cam_win.destroy()

        btn_start = tk.Button(
            btn_frame,
            text="Запустить камеру",
            command=start_camera,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_start.grid(row=0, column=0, padx=5)

        btn_capture = tk.Button(
            btn_frame,
            text="Сделать снимок",
            command=capture_photo,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_capture.grid(row=0, column=1, padx=5)

        btn_stop = tk.Button(
            btn_frame,
            text="Закрыть",
            command=stop_camera,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        )
        btn_stop.grid(row=0, column=2, padx=5)

    def show_channels(self):
        """Открывает окно выбора цветового канала."""
        if not self._validate_image_loaded():
            return

        channel_win = tk.Toplevel(self.root)
        channel_win.title("Цветовые каналы")
        channel_win.geometry(self.CHANNEL_WINDOW_SIZE)
        channel_win.configure(bg="#ffffff")

        tk.Label(
            channel_win,
            text="Выберите канал:",
            font=self.LABEL_FONT,
            bg="#ffffff"
        ).pack(pady=10)

        def show_channel(channel_idx, name):
            """Показывает один цветовой канал."""
            b, g, r = cv2.split(self.processed_image)

            if channel_idx == 0:  # Красный
                result = cv2.merge([np.zeros_like(b), np.zeros_like(g), r])
            elif channel_idx == 1:  # Зелёный
                result = cv2.merge([np.zeros_like(b), g, np.zeros_like(r)])
            else:  # Синий
                result = cv2.merge([b, np.zeros_like(g), np.zeros_like(r)])

            self._display_channel_in_window(result, name)

        btn_frame = tk.Frame(channel_win, bg="#ffffff")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Красный",
            command=lambda: show_channel(0, "Красный"),
            width=15,
            height=2,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Зелёный",
            command=lambda: show_channel(1, "Зелёный"),
            width=15,
            height=2,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame,
            text="Синий",
            command=lambda: show_channel(2, "Синий"),
            width=15,
            height=2,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        ).grid(row=0, column=2, padx=10)

    def crop_image(self):
        """Обрезает изображение по координатам пользователя."""
        if not self._validate_image_loaded():
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Обрезка изображения")
        dialog.geometry(self.CROP_DIALOG_SIZE)
        dialog.configure(bg="#ffffff")

        tk.Label(
            dialog,
            text="Введите координаты обрезки:",
            font=self.LABEL_FONT,
            bg="#ffffff"
        ).pack(pady=10)

        entries = {}
        labels_text = ["X1 (лево):", "Y1 (верх):", "X2 (право):", "Y2 (низ):"]
        defaults = ["0", "0", "", ""]

        for label_text, default in zip(labels_text, defaults):
            frame = tk.Frame(dialog, bg="#ffffff")
            frame.pack(pady=3)

            tk.Label(
                frame,
                text=label_text,
                width=12,
                anchor="w",
                bg="#ffffff"
            ).pack(side=tk.LEFT)

            entry = tk.Entry(frame, width=15)
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, padx=5)
            entries[label_text] = entry

        def apply_crop():
            """Применяет обрезку с проверкой координат."""
            try:
                x1 = int(entries["X1 (лево):"].get())
                y1 = int(entries["Y1 (верх):"].get())
                x2 = int(entries["X2 (право):"].get())
                y2 = int(entries["Y2 (низ):"].get())

                height, width = self.processed_image.shape[:2]

                if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
                    self._show_error("Координаты выходят за границы изображения")
                    return

                if x1 >= x2 or y1 >= y2:
                    self._show_error("X1 должен быть меньше X2, Y1 меньше Y2")
                    return

                self.processed_image = self.processed_image[y1:y2, x1:x2]
                self._display_image(self.processed_image)
                self.status_label.config(text="Обрезка выполнена")
                dialog.destroy()

            except ValueError:
                self._show_error("Введите числа")

        tk.Button(
            dialog,
            text="Применить",
            command=apply_crop,
            width=20,
            height=2,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        ).pack(pady=15)

    def adjust_brightness(self):
        """Изменяет яркость изображения."""
        if not self._validate_image_loaded():
            return

        value = simpledialog.askinteger(
            "Яркость",
            "Введите значение яркости (от -100 до 100):\n"
            "Положительное — светлее, отрицательное — темнее",
            initialvalue=30,
            minvalue=-100,
            maxvalue=100
        )

        if value is None:
            return

        self.processed_image = cv2.convertScaleAbs(
            self.processed_image,
            alpha=1,
            beta=value
        )
        self._display_image(self.processed_image)
        self.status_label.config(text=f"Яркость изменена на {value}")

    def draw_line(self):
        """Рисует зелёную линию по параметрам пользователя."""
        if not self._validate_image_loaded():
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Зелёная линия")
        dialog.geometry(self.LINE_DIALOG_SIZE)
        dialog.configure(bg="#ffffff")

        tk.Label(
            dialog,
            text="Параметры зелёной линии:",
            font=self.LABEL_FONT,
            bg="#ffffff"
        ).pack(pady=10)

        entries = {}
        labels_text = ["X1:", "Y1:", "X2:", "Y2:", "Толщина:"]
        defaults = ["0", "0", "", "", "2"]

        for label_text, default in zip(labels_text, defaults):
            frame = tk.Frame(dialog, bg="#ffffff")
            frame.pack(pady=3)

            tk.Label(
                frame,
                text=label_text,
                width=10,
                anchor="w",
                bg="#ffffff"
            ).pack(side=tk.LEFT)

            entry = tk.Entry(frame, width=15)
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, padx=5)
            entries[label_text] = entry

        def apply_line():
            """Рисует линию с проверкой параметров."""
            try:
                x1 = int(entries["X1:"].get())
                y1 = int(entries["Y1:"].get())
                x2 = int(entries["X2:"].get())
                y2 = int(entries["Y2:"].get())
                thickness = int(entries["Толщина:"].get())

                if thickness < 1:
                    self._show_error("Толщина должна быть не меньше 1")
                    return

                height, width = self.processed_image.shape[:2]

                if not (0 <= x1 < width and 0 <= y1 < height and
                        0 <= x2 < width and 0 <= y2 < height):
                    self._show_error(
                        f"Координаты за границами изображения!\n"
                        f"Ширина: {width}, Высота: {height}"
                    )
                    return

                if x1 == x2 and y1 == y2:
                    self._show_error("Начало и конец линии не могут совпадать")
                    return

                img_copy = self.processed_image.copy()
                cv2.line(
                    img_copy,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    thickness
                )

                self.processed_image = img_copy
                self._display_image(self.processed_image)
                self.status_label.config(text="Зелёная линия нарисована")
                dialog.destroy()

            except ValueError:
                self._show_error("Введите числа")
            except Exception as error:
                self._show_error(str(error))

        tk.Button(
            dialog,
            text="Нарисовать",
            command=apply_line,
            width=20,
            height=2,
            bg="#e0e0e0",
            relief="flat",
            bd=0
        ).pack(pady=15)

    def reset_image(self):
        """Сбрасывает изображение к исходному состоянию."""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self._display_image(self.processed_image)
            self.status_label.config(text="Изображение сброшено")


# ============================================================
# ЗАПУСК ПРОГРАММЫ
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
