import os
from decimal import Decimal
from datetime import datetime
from models import Car, Model, Sale, CarStatus, CarFullInfo, ModelSaleStats


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.cars_file = os.path.join(root_directory_path, 'cars.txt')
        self.cars_index_file = os.path.join(root_directory_path, 'cars_index.txt')
        self.models_file = os.path.join(root_directory_path, 'models.txt')
        self.models_index_file = os.path.join(root_directory_path, 'models_index.txt')
        self.sales_file = os.path.join(root_directory_path, 'sales.txt')
        self.sales_index_file = os.path.join(root_directory_path, 'sales_index.txt')

        # Инициализируем файлы, если их нет
        self._initialize_files()

    def _initialize_files(self):
        """Инициализируем файлы, если они не существуют."""
        # Инициализация файла с машинами
        if not os.path.exists(self.cars_file):
            with open(self.cars_file, 'w') as file:
                pass

        # Инициализация индекса машин
        if not os.path.exists(self.cars_index_file):
            with open(self.cars_index_file, 'w') as file:
                pass

        # Инициализация файла с моделями
        if not os.path.exists(self.models_file):
            with open(self.models_file, 'w') as file:
                pass

        # Инициализация индекса моделей
        if not os.path.exists(self.models_index_file):
            with open(self.models_index_file, 'w') as file:
                pass

        # Инициализация файла с продажами
        if not os.path.exists(self.sales_file):
            with open(self.sales_file, 'w') as file:
                pass

        # Инициализация индекса продаж
        if not os.path.exists(self.sales_index_file):
            with open(self.sales_index_file, 'w') as file:
                pass

    # Задание 1. Сохранение модели
    def add_model(self, model: Model) -> Model:
        # Добавляем модель в файл models.txt
        with open(self.models_file, 'a') as file:
            file.write(f"{model.name},{model.brand}\n")

        # Читаем текущие индексы
        with open(self.models_index_file, 'r') as file:
            index_lines = file.readlines()

        # Получаем индекс для новой модели
        new_index = f'{model.index()},{len(index_lines)}\n'

        # Добавляем индекс в правильное место
        index_lines.append(new_index)
        index_lines.sort()  # Индексы должны быть отсортированы

        # Перезаписываем файл индексов
        with open(self.models_index_file, 'w') as file:
            file.writelines(index_lines)

        return model

    # Задание 1. Сохранение автомобиля
    def add_car(self, car: Car) -> Car:
        # Добавляем автомобиль в файл cars.txt
        with open(self.cars_file, 'a') as file:
            file.write(f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}\n")

        # Читаем текущие индексы
        with open(self.cars_index_file, 'r') as file:
            index_lines = file.readlines()

        # Получаем индекс для нового автомобиля
        new_index = f'{car.index()},{len(index_lines)}\n'

        # Добавляем индекс в правильное место
        index_lines.append(new_index)
        index_lines.sort()  # Индексы должны быть отсортированы

        # Перезаписываем файл индексов
        with open(self.cars_index_file, 'w') as file:
            file.writelines(index_lines)

        return car

    # Задание 2. Сохранение продажи
    def sell_car(self, sale: Sale) -> Sale:
        # Чтение данных о машине из файла cars_index.txt
        with open(self.cars_index_file, 'r') as file:
            car_index_lines = file.readlines()

        # Поиск строки с VIN в файле cars_index.txt
        car_index_line = next((line for line in car_index_lines if sale.car_vin in line), None)
        if not car_index_line:
            raise ValueError(f"Car with VIN {sale.car_vin} not found in the car index.")

        car_index = int(car_index_line.split(',')[1].strip())  # Получаем индекс машины

        # Чтение данных о машинах из файла cars.txt
        with open(self.cars_file, 'r') as file:
            car_lines = file.readlines()

        # Получаем данные о машине по индексу
        car_data = car_lines[car_index].strip().split(',')  # Разделяем строку по запятой
        vin = car_data[0]
        model = car_data[1]
        price = float(car_data[2])
        date_start = car_data[3]
        status = car_data[4]

        # Обновляем статус автомобиля на "sold"
        car_lines[car_index] = f"{vin},{model},{price},{date_start},sold\n"

        # Сохраняем обновленные данные о машине в cars.txt
        with open(self.cars_file, 'r+') as file:  # 'r+' для чтения и записи
            file.seek(0)
            file.writelines(car_lines)  # Записываем обновленные строки

        # Записываем информацию о продаже в sales.txt
        with open(self.sales_file, 'a') as file:
            sale_data = f"{sale.sales_number},{sale.car_vin},{sale.sales_date},{sale.cost}\n"
            file.write(sale_data)  # Добавляем запись о продаже

        # Записываем индекс продажи в sales_index.txt
        with open(self.sales_index_file, 'a') as file:
            sale_index_data = f"{sale.sales_number},{len(open(self.sales_file).readlines())-1}\n"
            file.write(sale_index_data)  # Добавляем индекс продажи

        # Возвращаем объект Sale
        return sale

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        # Чтение файла cars.txt
        with open(self.cars_file, 'r') as file:
            car_lines = file.readlines()

        # Фильтрация машин по статусу
        available_cars = []
        for car_line in car_lines:
            try:
                # Разделяем строку по запятой
                car_data = car_line.strip().split(',')

                # Создаем объект Car на основе полученных данных
                vin = car_data[0]
                model_id = int(car_data[1])  # Предполагаем, что model - это ID модели
                price = Decimal(car_data[2])  # Преобразуем цену в Decimal
                date_start = datetime.strptime(car_data[3], "%Y-%m-%d %H:%M:%S")  # Преобразуем строку в datetime
                car_status = CarStatus(car_data[4])  # Преобразуем статус в соответствующий enum

                # Создаем объект Car
                car = Car(
                    vin=vin,
                    model=model_id,
                    price=price,
                    date_start=date_start,
                    status=car_status
                )

                # Проверяем, если статус автомобиля совпадает с переданным
                if car.status == status:
                    available_cars.append(car)
            except (IndexError, ValueError) as e:
                print(f"Ошибка при чтении данных о машине: {e}")
                continue

        # Сортировка автомобилей по VIN для обеспечения стабильного порядка
        available_cars.sort(key=lambda car: car.vin)

        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        try:
            # Чтение индекса автомобиля из файла cars_index.txt
            with open(self.cars_index_file, 'r') as file:
                car_index_lines = file.readlines()

            # Находим строку в файле cars_index.txt, соответствующую VIN
            car_index_line = next((line for line in car_index_lines if vin in line), None)
            if not car_index_line:
                print(f"Ошибка: Автомобиль с VIN {vin} не найден в индексном файле.")
                return None  # Если не нашли VIN, возвращаем None

            car_index = int(car_index_line.split(',')[1].strip())  # Получаем индекс машины

            # Чтение данных о машине из файла cars.txt
            with open(self.cars_file, 'r') as file:
                car_lines = file.readlines()

            # Получаем строку с данными о машине
            car_data = car_lines[car_index].strip().split(',')  # Разделяем строку по запятой
            vin = car_data[0]
            model = car_data[1]
            price = float(car_data[2])
            date_start = car_data[3]
            status = car_data[4]

            # Чтение файла models_index.txt для получения информации о модели
            with open(self.models_index_file, 'r') as file:
                models_index_lines = file.readlines()

            models_index_line = next((line for line in models_index_lines if str(model) in line), None)
            if not models_index_line:
                print(f"Ошибка: Модель для автомобиля с VIN {vin} не найдена в models_index.txt.")
                return None  # Если модель не найдена

            models_index = int(models_index_line.split(',')[1].strip())  # Индекс модели

            # Чтение файла models.txt
            with open(self.models_file, 'r') as file:
                model_lines = file.readlines()

            model_data = model_lines[models_index].strip().split(',')
            model_name = model_data[0]
            model_brand = model_data[1]

            # Чтение файла sales.txt для получения информации о продаже, если статус "sold"
            sales_date = None
            sales_cost = None
            if status == 'sold':
                with open(self.sales_file, 'r') as file:
                    sales_lines = file.readlines()

                sale_line = next((line for line in sales_lines if vin in line), None)
                if sale_line:
                    sale_data = sale_line.strip().split(',')
                    sales_date = sale_data[2]
                    sales_cost = float(sale_data[3])

            # Возвращаем информацию о машине с полным набором данных
            return CarFullInfo(
                vin=vin,
                car_model_name=model_name,
                car_model_brand=model_brand,
                price=price,
                date_start=date_start,
                status=status,
                sales_date=sales_date,
                sales_cost=sales_cost
            )

        except FileNotFoundError as e:
            print(f"Ошибка: Не удалось найти файл: {e.filename}")
            return None
        except Exception as e:
            print(f"Неизвестная ошибка при обработке данных для VIN {vin}: {e}")
            return None

# Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        # Шаг 1: Чтение индекса из файла cars_index.txt
        try:
            with open(self.cars_index_file, 'r') as file:
                index_lines = file.readlines()

            # Находим строку с VIN
            car_index_line = next((line for line in index_lines if vin in line), None)
            if not car_index_line:
                raise ValueError(f"Car with VIN {vin} not found in the index.")

            # Получаем индекс строки в файле cars.txt
            car_index = int(car_index_line.split(',')[1].strip())

            # Шаг 2: Чтение данных о машине из файла cars.txt
            with open(self.cars_file, 'r') as file:
                car_lines = file.readlines()

            # Получаем данные о машине по индексу
            car_data = car_lines[car_index].strip().split(',')
            # Обновляем VIN на новый
            car_data[0] = new_vin
            car_lines[car_index] = ','.join(car_data) + '\n'

            # Шаг 3: Обновляем индекс в cars_index.txt
            # Удаляем старую строку с индексом
            index_lines = [line for line in index_lines if vin not in line]
            # Добавляем новый индекс для нового VIN
            index_lines.append(f"{new_vin},{car_index}\n")

            # Сортируем индекс
            index_lines.sort()

            # Перезаписываем файлы
            with open(self.cars_file, 'w') as file:
                file.writelines(car_lines)

            with open(self.cars_index_file, 'w') as file:
                file.writelines(index_lines)

            # Шаг 4: Возвращаем обновленный объект Car
            vin = car_data[0]
            model = int(car_data[1])  # Предполагаем, что model - это ID
            price = Decimal(car_data[2])
            date_start = datetime.strptime(car_data[3], "%Y-%m-%d %H:%M:%S")
            status = CarStatus(car_data[4])

            updated_car = Car(vin=vin, model=model, price=price, date_start=date_start, status=status)
            return updated_car

        except ValueError as e:
            print(f"Ошибка: {e}")
            return None
        except FileNotFoundError as e:
            print(f"Ошибка: Не удалось найти файл: {e.filename}")
            return None
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return None

# Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        try:
            # Шаг 1: Чтение данных о продаже из файла sales.txt
            with open(self.sales_file, 'r') as file:
                sales_lines = file.readlines()

            # Находим строку с нужным номером продажи
            sale_line = next((line for line in sales_lines if sales_number in line), None)
            if not sale_line:
                raise ValueError(f"Sale with number {sales_number} not found.")

            # Получаем VIN автомобиля из строки продажи
            car_vin = sale_line.split(',')[1].strip()

            # Шаг 2: Чтение данных о машинах из файла cars.txt
            with open(self.cars_file, 'r') as file:
                car_lines = file.readlines()

            # Находим строку с автомобилем по VIN
            car_index_line = next((line for line in car_lines if car_vin in line), None)
            if not car_index_line:
                raise ValueError(f"Car with VIN {car_vin} not found.")

            car_index = car_lines.index(car_index_line)  # Индекс машины в cars.txt
            car_data = car_index_line.strip().split(',')
            car_data[4] = 'available'  # Восстановим статус машины на "available"
            car_lines[car_index] = ','.join(car_data) + '\n'

            # Шаг 3: Удаление записи из sales.txt (перезапись файла без этой строки)
            sales_lines = [line for line in sales_lines if sales_number not in line]

            with open(self.sales_file, 'w') as file:
                file.writelines(sales_lines)

            # Шаг 4: Запись изменений обратно в файл cars.txt
            with open(self.cars_file, 'w') as file:
                file.writelines(car_lines)

            # Возвращаем обновленный объект Car
            vin = car_data[0]
            model = int(car_data[1])  # Предполагаем, что model - это ID
            price = Decimal(car_data[2])
            date_start = datetime.strptime(car_data[3], "%Y-%m-%d %H:%M:%S")
            status = CarStatus(car_data[4])

            updated_car = Car(vin=vin, model=model, price=price, date_start=date_start, status=status)
            return updated_car

        except ValueError as e:
            print(f"Ошибка: {e}")
            return None
        except FileNotFoundError as e:
            print(f"Ошибка: Не удалось найти файл: {e.filename}")
            return None
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return None

# Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        # Шаг 1: Подсчитываем количество продаж по моделям
        sales_count_by_model = {}

        try:
            with open(self.sales_file, 'r') as file:
                sales_lines = file.readlines()

            for sale_line in sales_lines:
                # Извлекаем VIN и находим соответствующую модель
                sale_data = sale_line.strip().split(',')
                car_vin = sale_data[1]

                # Получаем модель для VIN из файла cars.txt
                with open(self.cars_index_file, 'r') as car_index_file:
                    car_index_lines = car_index_file.readlines()
                car_index_line = next((line for line in car_index_lines if car_vin in line), None)

                if car_index_line:
                    car_index = int(car_index_line.split(',')[1].strip())  # Индекс автомобиля
                    with open(self.cars_file, 'r') as car_file:
                        car_lines = car_file.readlines()
                    car_data = car_lines[car_index].strip().split(',')
                    car_model_id = int(car_data[1])

                    # Увеличиваем количество продаж для этой модели
                    if car_model_id not in sales_count_by_model:
                        sales_count_by_model[car_model_id] = 0
                    sales_count_by_model[car_model_id] += 1

        except FileNotFoundError as e:
            print(f"Ошибка: Не удалось найти файл: {e.filename}")
            return []

        # Шаг 2: Сортируем модели по количеству продаж, а затем по цене
        sorted_models = sorted(
            sales_count_by_model.items(),
            key=lambda x: (-x[1], -self.get_model_price(x[0]))  # Сначала по количеству, потом по цене
        )

        # Шаг 3: Чтение информации о моделях из models.txt для первых трех
        top_models = []
        for model_id, sales_count in sorted_models[:3]:
            try:
                with open(self.models_index_file, 'r') as model_index_file:
                    model_index_lines = model_index_file.readlines()
                model_index_line = next((line for line in model_index_lines if str(model_id) in line), None)
                if model_index_line:
                    model_index = int(model_index_line.split(',')[1].strip())

                    # Чтение файла models.txt
                    with open(self.models_file, 'r') as model_file:
                        model_lines = model_file.readlines()
                    model_data = model_lines[model_index].strip().split(',')
                    model_name = model_data[0]
                    model_brand = model_data[1]

                    # Создаем объект ModelSaleStats
                    model_sale_stats = ModelSaleStats(
                        car_model_name=model_name,
                        brand=model_brand,
                        sales_number=sales_count
                    )
                    top_models.append(model_sale_stats)

            except Exception as e:
                print(f"Ошибка при обработке модели с ID {model_id}: {e}")
                continue

        return top_models

    def get_model_price(self, model_id: int) -> Decimal:
        """Возвращает цену модели по ее ID"""
        try:
            with open(self.models_index_file, 'r') as file:
                model_index_lines = file.readlines()

            model_index_line = next((line for line in model_index_lines if str(model_id) in line), None)
            if model_index_line:
                model_index = int(model_index_line.split(',')[1].strip())

                with open(self.models_file, 'r') as file:
                    model_lines = file.readlines()
                model_data = model_lines[model_index].strip().split(',')
                # Предполагаем, что цена модели указывается в models.txt как второй параметр
                return Decimal(model_data[2])
            return Decimal(0)
        except Exception as e:
            print(f"Ошибка при получении цены модели с ID {model_id}: {e}")
            return Decimal(0)
