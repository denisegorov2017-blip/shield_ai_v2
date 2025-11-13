#!/usr/bin/env bash

set -e

JSON_MODE=false
SHORT_NAME=""
BRANCH_NUMBER=""
ARGS=()
i=1
while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --json) 
            JSON_MODE=true 
            ;;
        --short-name)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Ошибка: --short-name требует значения' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            # Проверить, является ли следующий аргумент другим параметром (начинается с --)
            if [[ "$next_arg" == --* ]]; then
                echo 'Ошибка: --short-name требует значения' >&2
                exit 1
            fi
            SHORT_NAME="$next_arg"
            ;;
        --number)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Ошибка: --number требует значения' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            if [[ "$next_arg" == --* ]]; then
                echo 'Ошибка: --number требует значения' >&2
                exit 1
            fi
            BRANCH_NUMBER="$next_arg"
            ;;
        --help|-h) 
            echo "Использование: $0 [--json] [--short-name <name>] [--number N] <описание_функции>"
            echo ""
            echo "Параметры:"
            echo "  --json              Вывод в формате JSON"
            echo "  --short-name <name> Указать краткое имя (2-4 слова) для ветки"
            echo "  --number N          Указать номер ветки вручную (переопределяет автоопределение)"
            echo "  --help, -h          Показать это справочное сообщение"
            echo ""
            echo "Примеры:"
            echo "  $0 'Добавить систему аутентификации пользователя' --short-name 'user-auth'"
            echo "  $0 'Реализовать интеграцию OAuth2 для API' --number 5"
            exit 0
            ;;
        *) 
            ARGS+=("$arg") 
            ;;
    esac
    i=$((i + 1))
done

FEATURE_DESCRIPTION="${ARGS[*]}"
if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "Использование: $0 [--json] [--short-name <name>] [--number N] <описание_функции>" >&2
    exit 1
fi

# Функция для поиска корня репозитория путем поиска существующих маркеров проекта
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.specify" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Функция для проверки существующих веток (локальных и удаленных) и возврата следующего доступного номера
check_existing_branches() {
    local short_name="$1"
    
    # Получить все удаленные репозитории для получения последней информации о ветках (подавить ошибки, если нет удаленных репозиториев)
    git fetch --all --prune 2>/dev/null || true
    
    # Найти все ветки, соответствующие шаблону, с помощью git ls-remote (более надежно)
    local remote_branches=$(git ls-remote --heads origin 2>/dev/null | grep -E "refs/heads/[0-9]+-${short_name}$" | sed 's/.*\/\([0-9]*\)-.*/\1/' | sort -n)
    
    # Также проверить локальные ветки
    local local_branches=$(git branch 2>/dev/null | grep -E "^[* ]*[0-9]+-${short_name}$" | sed 's/^[* ]*//' | sed 's/-.*//' | sort -n)
    
    # Также проверить каталог спецификаций
    local spec_dirs=""
    if [ -d "$SPECS_DIR" ]; then
        spec_dirs=$(find "$SPECS_DIR" -maxdepth 1 -type d -name "[0-9]*-${short_name}" 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/-.*//' | sort -n)
    fi
    
    # Объединить все источники и получить наибольшее число
    local max_num=0
    for num in $remote_branches $local_branches $spec_dirs; do
        if [ "$num" -gt "$max_num" ]; then
            max_num=$num
        fi
    done
    
    # Вернуть следующий номер
    echo $((max_num + 1))
}

# Определить корень репозитория. Предпочтительно использовать информацию git, но в случае сбоя
# выполнить поиск маркеров репозитория, чтобы рабочий процесс продолжал функционировать в репозиториях, которые
# были инициализированы с --no-git.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel)
    HAS_GIT=true
else
    REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
    if [ -z "$REPO_ROOT" ]; then
        echo "Ошибка: Не удалось определить корень репозитория. Пожалуйста, запустите этот скрипт изнутри репозитория." >&2
        exit 1
    fi
    HAS_GIT=false
fi

cd "$REPO_ROOT"

SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

# Функция для генерации имени ветки с фильтрацией стоп-слов и фильтрацией по длине
generate_branch_name() {
    local description="$1"
    
    # Распространенные стоп-слова для фильтрации
    local stop_words="^(i|a|an|the|to|for|of|in|on|at|by|with|from|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might|must|shall|this|that|these|those|my|your|our|their|want|need|add|get|set)$"
    
    # Преобразовать в нижний регистр и разделить на слова
    local clean_name=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/ /g')
    
    # Фильтровать слова: удалить стоп-слова и слова короче 3 символов (если только они не являются заглавными акронимами в оригинале)
    local meaningful_words=()
    for word in $clean_name; do
        # Пропустить пустые слова
        [ -z "$word" ] && continue
        
        # Сохранить слова, которые НЕ являются стоп-словами И (длина >= 3 ИЛИ потенциальные акронимы)
        if ! echo "$word" | grep -qiE "$stop_words"; then
            if [ ${#word} -ge 3 ]; then
                meaningful_words+=("$word")
            elif echo "$description" | grep -q "\b${word^^}\b"; then
                # Сохранить короткие слова, если они встречаются в верхнем регистре в оригинале (вероятно, акронимы)
                meaningful_words+=("$word")
            fi
        fi
    done
    
    # Если у нас есть значимые слова, использовать первые 3-4 из них
    if [ ${#meaningful_words[@]} -gt 0 ]; then
        local max_words=3
        if [ ${#meaningful_words[@]} -eq 4 ]; then max_words=4; fi
        
        local result=""
        local count=0
        for word in "${meaningful_words[@]}"; do
            if [ $count -ge $max_words ]; then break; fi
            if [ -n "$result" ]; then result="$result-"; fi
            result="$result$word"
            count=$((count + 1))
        done
        echo "$result"
    else
        # Резервная логика, если значимые слова не найдены
        echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//' | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//'
    fi
}

# Сгенерировать имя ветки
if [ -n "$SHORT_NAME" ]; then
    # Использовать предоставленное краткое имя, просто очистить его
    BRANCH_SUFFIX=$(echo "$SHORT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
else
    # Генерировать из описания с умной фильтрацией
    BRANCH_SUFFIX=$(generate_branch_name "$FEATURE_DESCRIPTION")
fi

# Определить номер ветки
if [ -z "$BRANCH_NUMBER" ]; then
    if [ "$HAS_GIT" = true ]; then
        # Проверить существующие ветки на удаленных репозиториях
        BRANCH_NUMBER=$(check_existing_branches "$BRANCH_SUFFIX")
    else
        # Возврат к проверке локального каталога
        HIGHEST=0
        if [ -d "$SPECS_DIR" ]; then
            for dir in "$SPECS_DIR"/*; do
                [ -d "$dir" ] || continue
                dirname=$(basename "$dir")
                number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
                number=$((10#$number))
                if [ "$number" -gt "$HIGHEST" ]; then HIGHEST=$number; fi
            done
        fi
        BRANCH_NUMBER=$((HIGHEST + 1))
    fi
fi

FEATURE_NUM=$(printf "%03d" "$BRANCH_NUMBER")
BRANCH_NAME="${FEATURE_NUM}-${BRANCH_SUFFIX}"

# GitHub требует ограничение в 244 байта на имена веток
# Проверить и усечь при необходимости
MAX_BRANCH_LENGTH=244
if [ ${#BRANCH_NAME} -gt $MAX_BRANCH_LENGTH ]; then
    # Рассчитать, сколько нужно усечь из суффикса
    # Учесть: номер функции (3) + дефис (1) = 4 символа
    MAX_SUFFIX_LENGTH=$((MAX_BRANCH_LENGTH - 4))
    
    # Усечь суффикс до границы слова, если возможно
    TRUNCATED_SUFFIX=$(echo "$BRANCH_SUFFIX" | cut -c1-$MAX_SUFFIX_LENGTH)
    # Удалить конечный дефис, если усечение создало его
    TRUNCATED_SUFFIX=$(echo "$TRUNCATED_SUFFIX" | sed 's/-$//')
    
    ORIGINAL_BRANCH_NAME="$BRANCH_NAME"
    BRANCH_NAME="${FEATURE_NUM}-${TRUNCATED_SUFFIX}"
    
    >&2 echo "[specify] Предупреждение: Имя ветки превысило ограничение GitHub в 244 байта"
    >&2 echo "[specify] Оригинал: $ORIGINAL_BRANCH_NAME (${#ORIGINAL_BRANCH_NAME} байт)"
    >&2 echo "[specify] Усечено до: $BRANCH_NAME (${#BRANCH_NAME} байт)"
fi

if [ "$HAS_GIT" = true ]; then
    git checkout -b "$BRANCH_NAME"
else
    >&2 echo "[specify] Предупреждение: Git-репозиторий не обнаружен; пропущено создание ветки для $BRANCH_NAME"
fi

FEATURE_DIR="$SPECS_DIR/$BRANCH_NAME"
mkdir -p "$FEATURE_DIR"

TEMPLATE="$REPO_ROOT/.specify/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then cp "$TEMPLATE" "$SPEC_FILE"; else touch "$SPEC_FILE"; fi

# Установить переменную окружения SPECIFY_FEATURE для текущей сессии
export SPECIFY_FEATURE="$BRANCH_NAME"

if $JSON_MODE; then
    printf '{"BRANCH_NAME":"%s","SPEC_FILE":"%s","FEATURE_NUM":"%s"}\n' "$BRANCH_NAME" "$SPEC_FILE" "$FEATURE_NUM"
else
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "Переменная окружения SPECIFY_FEATURE установлена в: $BRANCH_NAME"
fi
