# Шпаргалка по Git

## Настройка (один раз)
```bash
# Задать имя пользователя
git config --global user.name "Имя"

# Задать email
git config --global user.email "email"
```

## Начало работы
```bash
# Создать репозиторий в папке
git init

# Скачать репозиторий с GitHub
git clone <url>
```

## Ежедневная работа
```bash
# Показать что изменилось
git status

# Добавить все файлы в очередь
git add .

# Добавить конкретный файл
git add file.py

# Сохранить снимок с описанием
git commit -m "описание изменений"

# Отправить на GitHub
git push

# Скачать изменения с GitHub
git pull
```

## Быстрый пуш (3 команды)
```bash
# Добавить изменения
git add .

# Сделать коммит
git commit -m "описание изменений"

# Запушить
git push
```

## История
```bash
# Полная история коммитов
git log

# Краткая история (ID + сообщение)
git log --oneline

# Показать что изменилось в файлах
git diff
```

## Откат
```bash
# Отменить все несохранённые изменения
git checkout .

# Перейти к конкретному коммиту
git checkout <ID>

# Откатить проект к коммиту (удалит всё после)
git reset --hard <ID>

# Отменить коммит не удаляя историю
git revert <ID>
```

## Ветки
```bash
# Список веток
git branch

# Создать ветку
git branch new-feat

# Переключиться на ветку
git checkout new-feat

# Слить ветку в текущую
git merge new-feat
```

## Связь с GitHub
```bash
# Показать адрес репозитория
git remote -v

# Подключить GitHub
git remote add origin <url>

# Изменить адрес
git remote set-url origin <url>
```
