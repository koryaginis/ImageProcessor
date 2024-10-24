import os
import concurrent.futures
from urllib3 import request
from pathlib import Path
import time
from PIL import Image
from queue import Queue

from concurrent.futures import ThreadPoolExecutor

threads_count = 1 # Количество потоков
intensity_threshold = 128 # Порог интенсивности
dilation_step = 1

# Указание пути к исходным файлам
img_folder = Path("D:\\PP\\Task-2\\images")

def main():

    print(f"\nКоличество потоков: {threads_count}\n")

    main_start_time = time.time()

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

    main_end_time = time.time()

    print(f"Общее время работы программы составило {(main_end_time - main_start_time)} секунд")

def img_processor(img_name):

    # Начало отсчета времени выполнения программы
    start_time = time.time()

    print("Обработка файла " + img_name + "...")

    img_intencity_processor_output = intencity_processor(img_name)

    img_intencity_processor_output.save(f'D:\PP\Task-2\images\output\{os.path.splitext(img_name)[0]}_intencity_processor.jpg')

    img_color_array = img_to_color_array(img_intencity_processor_output)

    img_dilation_processor_output = dilation_processor(img_color_array, img_intencity_processor_output)

    img_output = color_array_to_img(img_dilation_processor_output)

    img_output.save(f'D:\PP\Task-2\images\output\{os.path.splitext(img_name)[0]}_dilation_processor.jpg')

    # Конец отсчета времени выполнения программы
    end_time = time.time()

    # Вывод в терминал значения времени выполнения программы
    print(f"Время обработки {img_name} составило {(end_time - start_time)} секунд\n")

def process_row(img_name, img_folder, intensity_threshold, y, result_queue):
    img = Image.open(os.path.join(img_folder, img_name))
    width, height = img.size
    img_output = Image.new("L", (width, 1))

    for x in range(width):
        r, g, b = img.getpixel((x, y))
        intensity = (r + g + b) // 3
        intensity_output = 0 if intensity < intensity_threshold else 255
        img_output.putpixel((x, 0), intensity_output)

    result_queue.put((y, img_output))

def intencity_processor(img_name):
    img = Image.open(os.path.join(img_folder, img_name))
    width, height = img.size
    img_output = Image.new("L", (width, height))
    result_queue = Queue()

    with ThreadPoolExecutor(max_workers = threads_count) as executor:
        for y in range(height):
            executor.submit(process_row, img_name, img_folder, intensity_threshold, y, result_queue)

    while not result_queue.empty():
        y, result_img = result_queue.get()
        img_output.paste(result_img, (0, y))

    return img_output

def img_to_color_array(img):
    
    # Получаем размеры изображения
    width, height = img.size
    
    # Создаем пустой двумерный массив для хранения цветовых значений
    color_array = [[None for _ in range(height)] for _ in range(width)]
    
    # Получаем цвет каждого пикселя изображения и сохраняем его в массиве
    for i in range(width):
        for j in range(height):
            color_array[i][j] = img.getpixel((i, j))
    
    return color_array

def dilation_processor(color_array, img):

    width = len(color_array)
    height = len(color_array[0])
    result_color_array = [[None for _ in range(height)] for _ in range(width)]

    for i in range(width):
        for j in range(height):
            color = color_array[i][j]
            intensity = img.getpixel((i, j))

            if intensity >= intensity_threshold:
                start_x = i - dilation_step
                start_y = j - dilation_step
                end_x = i + dilation_step
                end_y = j + dilation_step

                for x in range(start_x, end_x):
                    for y in range(start_y, end_y):
                        if x >= 0 and y >= 0 and x < width and y < height:
                            result_color_array[x][y] = (255, 255, 255)
            elif result_color_array[i][j] is None:
                result_color_array[i][j] = (0, 0, 0)

    return result_color_array

def color_array_to_img(color_array):
    # Получаем размеры массива
    width = len(color_array)
    height = len(color_array[0])
    
    # Создаем новое изображение
    img = Image.new("RGB", (width, height))
    
    # Записываем цветовые значения из массива в изображение
    for i in range(width):
        for j in range(height):
            img.putpixel((i, j), color_array[i][j])
    
    return img

if __name__ == "__main__":
    main()
