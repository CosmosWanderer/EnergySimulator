# Симулятор энергосети

## Запуск
```
# Создать и активировать окружение
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Установить зависимости
pip install -r requirements.txt

# Тест с избытком генерации (brute force)
python simulator.py tests/test_surplus.json

# Тест с дефицитом генерации (brute force)
python simulator.py tests/test_deficit.json

# С DP алгоритмом
python simulator.py tests/test_surplus.json --method dp
python simulator.py tests/test_deficit.json --method dp
```

## Зависимости
```
python3.14.3
```

## Описание решения

## Допущения и упрощения

## Возможные расширения

## Использование ИИ