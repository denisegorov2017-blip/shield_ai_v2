#!/bin/bash
# fix_markdownlint_errors_safe.sh
# Скрипт для автоматического безопасного исправления основных ошибок markdownlint с учетом структуры Markdown

echo "Запуск mdformat для автоформатирования всех Markdown-файлов..."
find . -name "*.md" -exec mdformat {} \;

echo "Проверка ошибок markdownlint..."
markdown_files=$(find . -name "*.md")
lint_output=$(markdownlint $markdown_files)

# MD041: Первая строка должна быть заголовком верхнего уровня
echo "Исправление ошибок MD041 (First line should be h1 heading)..."
for file in $markdown_files; do
    first_line=$(head -n 1 "$file")
    if [[ ! $first_line =~ ^\# ]]; then
        sed -i '1s;^;# Заголовок;\n;' "$file"
        echo "Добавлен заголовок в $file"
    fi
done

# MD026: Заголовки не должны заканчиваться знаками препинания
echo "Исправление ошибок MD026 (Trailing punctuation in headings)..."
for file in $markdown_files; do
    sed -i -E '/^#+.*[\.\!\:\;\,\?]$/s/([\.\!\:\;\,\?])$//' "$file"
done

# MD040: Для fenced code block указывай язык (по умолчанию python)
echo "Исправление ошибок MD040 (Fenced code blocks need language)..."
for file in $markdown_files; do
    # только для пустых блоков кода, не затрагивая существующие языки
    sed -i 's/^````python/' "$file"
    sed -i 's/^``````python/' "$file"
done

# MD031: Пустые строки вокруг блоков кода
echo "Исправление ошибок MD031 (Blanks around fenced code)..."
for file in $markdown_files; do
    # Добавить пустую строку перед блоком кода, если нет
    awk '
    BEGIN {codeblock=0}
    /^```/ {
        if (codeblock==0) {
            if (NR > 1 && prev != "") print ""
            codeblock=1
        } else {
            codeblock=0
        }
    }
    {print; prev=$0}
    ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done

echo "MD013 (Line length) НЕ выполняется автоматом: перенос строк во всех типах блоков может нарушить Markdown-структуру и читаемость."
echo "Рекомендуется ПРОСМОТРЕТЬ вручную все длинные строки только в обычных текстовых абзацах."

# MD033: Встроенный HTML — только предупреждение
for file in $markdown_files; do
    if grep -qE '<[a-z][\s\S]*>' "$file"; then
        echo "Внимание! В $file обнаружен встроенный HTML. Для MD033 требуется ручная правка."
    fi
done

echo "Форматирование завершено!"
echo "Повторно запусти markdownlint для контроля. MD013 и MD033 требуют корректировки вручную."