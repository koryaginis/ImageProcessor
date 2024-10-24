from PIL import Image
from PIL import ImageFilter
from PIL import Image
import numpy as np
import time
from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

# Указание пути к с исходным файлам
img_folder = Path("D:\\PP\\Task-2\\images")

threads_count = 1 # Количество потоков

def main():
  

    main_start_time = time.time()

    print(f"\nКоличество потоков: {threads_count}")

    try:
        # Допустимые расширения файлов для обработки (изображения)
        img_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

        # Получение из папки списка изображений с фильтрацией по допустимым расширениям
        img_list = [img_name for img_name in os.listdir(img_folder) if os.path.splitext(img_name)[1].lower() in img_extensions]

        # Обработка каждого изображения в списке последовательно
        for img_name in img_list:
            img_processor(img_name)

    except Exception as e:
        print(e)
        raise(e)

    main_end_time = time.time()

    print(f"Общее время работы программы составило {(main_end_time - main_start_time)} секунд")

def img_processor(img_name):

  image = Image.open(os.path.join(img_folder, img_name))

  print("\nОбработка файла " + img_name + "...")

  # Объявление переменной для записи суммы времени работы всех запусков программы
  total_time = 0

  # Запуск цикла для троекратного выполнения программы
  for run in range(3):

    # Начало отсчета времени выполнения программы
    start_time = time.time()

    # Создание матрицы конволюции для придания исходному изображению рельефа
    emboss_kernel = np.array([[-2, -1, 0],
                            [-1, 1, 1],
                            [0, 1, 2]])

    # Применение свертки для каждого цветового канала
    red_channel = image.split()[0].filter(ImageFilter.Kernel((3, 3), emboss_kernel.flatten()))
    green_channel = image.split()[1].filter(ImageFilter.Kernel((3, 3), emboss_kernel.flatten()))
    blue_channel = image.split()[2].filter(ImageFilter.Kernel((3, 3), emboss_kernel.flatten()))

    # Объединение каналов
    embossed_image = Image.merge('RGB', (red_channel, green_channel, blue_channel))

    # Проход по каждому пикселю изображения
    def process_row(result_queue, input_row, i, y_total):
        
        input_width, input_height = input_row.size

        output_row = Image.new('RGB', (input_width // 2, input_height // 2))

        y = 0

        for x in range(0, input_width, 2):

            # Вычисление средних значений цветовых компонент
            avg_color = (
                (input_row.getpixel((x, y))[0] + input_row.getpixel((x + 1, y))[0] +
                input_row.getpixel((x, y + 1))[0] + input_row.getpixel((x + 1, y + 1))[0]) // 4,

                (input_row.getpixel((x, y))[1] + input_row.getpixel((x + 1, y))[1] +
                input_row.getpixel((x, y + 1))[1] + input_row.getpixel((x + 1, y + 1))[1]) // 4,

                (input_row.getpixel((x, y))[2] + input_row.getpixel((x + 1, y))[2] +
                input_row.getpixel((x, y + 1))[2] + input_row.getpixel((x + 1, y + 1))[2]) // 4
            )

            output_row.putpixel((x // 2, 0), avg_color)

        result_queue.put((output_row, i))

    def scaling(img_name, embossed_image, image_rows):
        
        # Получение размеров исходного изображения
        input_width, input_height = embossed_image.size

        # Создание нового изображения для масштабирования изображения с рельефом
        output = Image.new('RGB', (input_width // 2, input_height // 2))

        output_rows_array = []  # Создаем пустой массив для хранения результатов

        result_queue = Queue()

        with ThreadPoolExecutor(max_workers = threads_count) as executor:
            for y in range(0, input_height, 2):
                i = y//2
                executor.submit(process_row, result_queue, image_rows[i], i, y)

        while not result_queue.empty():
            output_row = result_queue.get()
            output_rows_array.append((output_row))

        return output_rows_array
    
    image_rows = split_image(embossed_image)
    
    scaled_array = scaling(img_name, embossed_image, image_rows)

    output = merge(scaled_array)

    output.save(f'D:\PP\Task-2\images\output\{os.path.splitext(img_name)[0]}_output.jpg')

    # Конец отсчета времени выполнения программы
    end_time = time.time()

    # Вывод в терминал значения времени выполнения программы
    execution_time = end_time - start_time
    print(f"Время выполнения {run + 1} запуска программы составляет {execution_time} секунд")

    total_time += execution_time

  print(f"Среднее время работы программы составляет {total_time / 3} секунд \n")

def split_image(image):
    img_width, img_height = image.size
    image_rows = []

    for y in range(0, img_height, 2):
        # Извлекаем строку изображения высотой 2 пикселя
        row = image.crop((0, y, img_width, min(y + 2, img_height)))
        image_rows.append(row)

    return image_rows

def merge(scaled_array):
    # Проверяем, пуст ли массив
    if len(scaled_array) == 0:
        return None
    
    # Получаем ширину изображения
    width = scaled_array[0][0].width
    height = len(scaled_array)
    
    # Создаем пустое изображение для объединенного изображения
    full_image = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # Объединяем части изображения
    for i, part in enumerate(scaled_array):
        full_image.paste(part[0], (0, i))
    
    # Показываем объединенное изображение
    return full_image

if __name__ == "__main__":
    main()
