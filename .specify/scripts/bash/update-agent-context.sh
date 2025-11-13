#!/usr/bin/env bash

# Обновление файлов контекста агента с информацией из plan.md
#
# Этот скрипт поддерживает файлы контекста агентов ИИ, разбирая спецификации функций
# и обновляя файлы конфигурации агентов с информацией о проекте.
#
# ОСНОВНЫЕ ФУНКЦИИ:
# 1. Проверка окружения
#    - Проверяет структуру репозитория git и информацию о ветке
#    - Проверяет наличие необходимых файлов plan.md и шаблонов
#    - Проверяет права доступа к файлам
#
# 2. Извлечение данных из плана
#    - Разбирает файлы plan.md для извлечения метаданных проекта
#    - Определяет язык/версию, фреймворки, базы данных и типы проектов
#    - Корректно обрабатывает отсутствующие или неполные данные спецификации
#
# 3. Управление файлами агента
#    - Создает новые файлы контекста агента из шаблонов при необходимости
#    - Обновляет существующие файлы агента новой информацией о проекте
#    - Сохраняет ручные добавления и пользовательские конфигурации
#    - Поддерживает несколько форматов агентов ИИ и структур каталогов
#
# 4. Генерация контента
#    - Генерирует команды сборки/тестирования, специфичные для языка
#    - Создает соответствующие структуры каталогов проекта
#    - Обновляет разделы стека технологий и недавних изменений
#    - Поддерживает последовательное форматирование и временные метки
#
# 5. Поддержка нескольких агентов
#    - Обрабатывает специфичные пути файлов агента и соглашения об именовании
#    - Поддерживает: Claude, Gemini, Copilot, Cursor, Qwen, opencode, Codex, Windsurf, Kilo Code, Auggie CLI, Roo Code, CodeBuddy CLI, Amp или Amazon Q Developer CLI
#    - Может обновлять одного агента или все существующие файлы агента
#    - Создает файл Claude по умолчанию, если файлы агента не существуют
#
# Использование: ./update-agent-context.sh [agent_type]
# Типы агентов: claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|q
# Оставьте пустым для обновления всех существующих файлов агента

set -e

# Включить строгую обработку ошибок
set -u
set -o pipefail

#==============================================================================
# Конфигурация и глобальные переменные
#==============================================================================

# Получить каталог скрипта и загрузить общие функции
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Получить все пути и переменные из общих функций
eval $(get_feature_paths)

NEW_PLAN="$IMPL_PLAN"  # Псевдоним для совместимости с существующим кодом
AGENT_TYPE="${1:-}"

# Специфичные пути к файлам агента  
CLAUDE_FILE="$REPO_ROOT/CLAUDE.md"
GEMINI_FILE="$REPO_ROOT/GEMINI.md"
COPILOT_FILE="$REPO_ROOT/.github/copilot-instructions.md"
CURSOR_FILE="$REPO_ROOT/.cursor/rules/specify-rules.mdc"
QWEN_FILE="$REPO_ROOT/QWEN.md"
AGENTS_FILE="$REPO_ROOT/AGENTS.md"
WINDSURF_FILE="$REPO_ROOT/.windsurf/rules/specify-rules.md"
KILOCODE_FILE="$REPO_ROOT/.kilocode/rules/specify-rules.md"
AUGGIE_FILE="$REPO_ROOT/.augment/rules/specify-rules.md"
ROO_FILE="$REPO_ROOT/.roo/rules/specify-rules.md"
CODEBUDDY_FILE="$REPO_ROOT/CODEBUDDY.md"
AMP_FILE="$REPO_ROOT/AGENTS.md"
Q_FILE="$REPO_ROOT/AGENTS.md"

# Файл шаблона
TEMPLATE_FILE="$REPO_ROOT/.specify/templates/agent-file-template.md"

# Глобальные переменные для разобранных данных плана
NEW_LANG=""
NEW_FRAMEWORK=""
NEW_DB=""
NEW_PROJECT_TYPE=""

#==============================================================================
# Вспомогательные функции
#==============================================================================

log_info() {
    echo "INFO: $1"
}

log_success() {
    echo "✓ $1"
}

log_error() {
    echo "ERROR: $1" >&2
}

log_warning() {
    echo "WARNING: $1" >&2
}

# Функция очистки для временных файлов
cleanup() {
    local exit_code=$?
    rm -f /tmp/agent_update_*_$$
    rm -f /tmp/manual_additions_$$
    exit $exit_code
}

# Настроить ловушку очистки
trap cleanup EXIT INT TERM

#==============================================================================
# Функции проверки
#==============================================================================

validate_environment() {
    # Проверить, есть ли у нас текущая ветка/функция (git или без git)
    if [[ -z "$CURRENT_BRANCH" ]]; then
        log_error "Невозможно определить текущую функцию"
        if [[ "$HAS_GIT" == "true" ]]; then
            log_info "Убедитесь, что вы находитесь на ветке функции"
        else
            log_info "Установите переменную окружения SPECIFY_FEATURE или создайте функцию сначала"
        fi
        exit 1
    fi
    
    # Проверить, существует ли plan.md
    if [[ ! -f "$NEW_PLAN" ]]; then
        log_error "Файл plan.md не найден в $NEW_PLAN"
        log_info "Убедитесь, что вы работаете над функцией с соответствующим каталогом спецификации"
        if [[ "$HAS_GIT" != "true" ]]; then
            log_info "Используйте: export SPECIFY_FEATURE=имя-вашей-функции или создайте новую функцию сначала"
        fi
        exit 1
    fi
    
    # Проверить, существует ли шаблон (нужен для новых файлов)
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_warning "Файл шаблона не найден в $TEMPLATE_FILE"
        log_warning "Создание новых файлов агента завершится ошибкой"
    fi
}

#==============================================================================
# Функции разбора плана
#==============================================================================

extract_plan_field() {
    local field_pattern="$1"
    local plan_file="$2"
    
    grep "^\*\*${field_pattern}\*\*: " "$plan_file" 2>/dev/null | \
        head -1 | \
        sed "s|^\*\*${field_pattern}\*\*: ||" | \
        sed 's/^[ \t]*//;s/[ \t]*$//' | \
        grep -v "NEEDS CLARIFICATION" | \
        grep -v "^N/A$" || echo ""
}

parse_plan_data() {
    local plan_file="$1"
    
    if [[ ! -f "$plan_file" ]]; then
        log_error "Файл плана не найден: $plan_file"
        return 1
    fi
    
    if [[ ! -r "$plan_file" ]]; then
        log_error "Файл плана не читается: $plan_file"
        return 1
    fi
    
    log_info "Разбор данных плана из $plan_file"
    
    NEW_LANG=$(extract_plan_field "Language/Version" "$plan_file")
    NEW_FRAMEWORK=$(extract_plan_field "Primary Dependencies" "$plan_file")
    NEW_DB=$(extract_plan_field "Storage" "$plan_file")
    NEW_PROJECT_TYPE=$(extract_plan_field "Project Type" "$plan_file")
    
    # Записать в лог, что мы нашли
    if [[ -n "$NEW_LANG" ]]; then
        log_info "Найден язык: $NEW_LANG"
    else
        log_warning "Информация о языке не найдена в плане"
    fi
    
    if [[ -n "$NEW_FRAMEWORK" ]]; then
        log_info "Найден фреймворк: $NEW_FRAMEWORK"
    fi
    
    if [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]]; then
        log_info "Найдена база данных: $NEW_DB"
    fi
    
    if [[ -n "$NEW_PROJECT_TYPE" ]]; then
        log_info "Найден тип проекта: $NEW_PROJECT_TYPE"
    fi
}

format_technology_stack() {
    local lang="$1"
    local framework="$2"
    local parts=()
    
    # Добавить непустые части
    [[ -n "$lang" && "$lang" != "NEEDS CLARIFICATION" ]] && parts+=("$lang")
    [[ -n "$framework" && "$framework" != "NEEDS CLARIFICATION" && "$framework" != "N/A" ]] && parts+=("$framework")
    
    # Объединить с правильным форматированием
    if [[ ${#parts[@]} -eq 0 ]]; then
        echo ""
    elif [[ ${#parts[@]} -eq 1 ]]; then
        echo "${parts[0]}"
    else
        # Объединить несколько частей с " + "
        local result="${parts[0]}"
        for ((i=1; i<${#parts[@]}; i++)); do
            result="$result + ${parts[i]}"
        done
        echo "$result"
    fi
}

#==============================================================================
# Функции генерации шаблона и контента
#==============================================================================

get_project_structure() {
    local project_type="$1"
    
    if [[ "$project_type" == *"web"* ]]; then
        echo "backend/\\nfrontend/\\ntests/"
    else
        echo "src/\\ntests/"
    fi
}

get_commands_for_language() {
    local lang="$1"
    
    case "$lang" in
        *"Python"*)
            echo "cd src && pytest && ruff check ."
            ;;
        *"Rust"*)
            echo "cargo test && cargo clippy"
            ;;
        *"JavaScript"*|*"TypeScript"*)
            echo "npm test \\&\\& npm run lint"
            ;;
        *)
            echo "# Добавить команды для $lang"
            ;;
    esac
}

get_language_conventions() {
    local lang="$1"
    echo "$lang: Следовать стандартным соглашениям"
}

create_new_agent_file() {
    local target_file="$1"
    local temp_file="$2"
    local project_name="$3"
    local current_date="$4"
    
    if [[ ! -f "$TEMPLATE_FILE" ]]; then
        log_error "Шаблон не найден в $TEMPLATE_FILE"
        return 1
    fi
    
    if [[ ! -r "$TEMPLATE_FILE" ]]; then
        log_error "Файл шаблона не читается: $TEMPLATE_FILE"
        return 1
    fi
    
    log_info "Создание нового файла контекста агента из шаблона..."
    
    if ! cp "$TEMPLATE_FILE" "$temp_file"; then
        log_error "Не удалось скопировать файл шаблона"
        return 1
    fi
    
    # Заменить заполнители шаблона
    local project_structure
    project_structure=$(get_project_structure "$NEW_PROJECT_TYPE")
    
    local commands
    commands=$(get_commands_for_language "$NEW_LANG")
    
    local language_conventions
    language_conventions=$(get_language_conventions "$NEW_LANG")
    
    # Выполнить подстановки с проверкой ошибок с использованием более безопасного подхода
    # Экранировать специальные символы для sed, используя другой разделитель или экранирование
    local escaped_lang=$(printf '%s\n' "$NEW_LANG" | sed 's/[\[\.*^$()+{}|]/\\&/g')
    local escaped_framework=$(printf '%s\n' "$NEW_FRAMEWORK" | sed 's/[\[\.*^$()+{}|]/\\&/g')
    local escaped_branch=$(printf '%s\n' "$CURRENT_BRANCH" | sed 's/[\[\.*^$()+{}|]/\\&/g')
    
    # Условно построить строки стека технологий и недавних изменений
    local tech_stack
    if [[ -n "$escaped_lang" && -n "$escaped_framework" ]]; then
        tech_stack="- $escaped_lang + $escaped_framework ($escaped_branch)"
    elif [[ -n "$escaped_lang" ]]; then
        tech_stack="- $escaped_lang ($escaped_branch)"
    elif [[ -n "$escaped_framework" ]]; then
        tech_stack="- $escaped_framework ($escaped_branch)"
    else
        tech_stack="- ($escaped_branch)"
    fi

    local recent_change
    if [[ -n "$escaped_lang" && -n "$escaped_framework" ]]; then
        recent_change="- $escaped_branch: Добавлено $escaped_lang + $escaped_framework"
    elif [[ -n "$escaped_lang" ]]; then
        recent_change="- $escaped_branch: Добавлено $escaped_lang"
    elif [[ -n "$escaped_framework" ]]; then
        recent_change="- $escaped_branch: Добавлено $escaped_framework"
    else
        recent_change="- $escaped_branch: Добавлено"
    fi

    local substitutions=(
        "s|\[PROJECT NAME\]|$project_name|"
        "s|\[DATE\]|$current_date|"
        "s|\[EXTRACTED FROM ALL PLAN.MD FILES\]|$tech_stack|"
        "s|\[ACTUAL STRUCTURE FROM PLANS\]|$project_structure|g"
        "s|\[ONLY COMMANDS FOR ACTIVE TECHNOLOGIES\]|$commands|"
        "s|\[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE\]|$language_conventions|"
        "s|\[LAST 3 FEATURES AND WHAT THEY ADDED\]|$recent_change|"
    )
    
    for substitution in "${substitutions[@]}"; do
        if ! sed -i.bak -e "$substitution" "$temp_file"; then
            log_error "Не удалось выполнить подстановку: $substitution"
            rm -f "$temp_file" "$temp_file.bak"
            return 1
        fi
    done
    
    # Преобразовать последовательности \n в реальные символы новой строки
    newline=$(printf '\n')
    sed -i.bak2 "s/\\\\n/${newline}/g" "$temp_file"
    
    # Очистить резервные файлы
    rm -f "$temp_file.bak" "$temp_file.bak2"
    
    return 0
}



update_existing_agent_file() {
    local target_file="$1"
    local current_date="$2"
    
    log_info "Обновление существующего файла контекста агента..."
    
    # Использовать один временный файл для атомарного обновления
    local temp_file
    temp_file=$(mktemp) || {
        log_error "Не удалось создать временный файл"
        return 1
    }
    
    # Обработать файл за один проход
    local tech_stack=$(format_technology_stack "$NEW_LANG" "$NEW_FRAMEWORK")
    local new_tech_entries=()
    local new_change_entry=""
    
    # Подготовить новые записи технологий
    if [[ -n "$tech_stack" ]] && ! grep -q "$tech_stack" "$target_file"; then
        new_tech_entries+=("- $tech_stack ($CURRENT_BRANCH)")
    fi
    
    if [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]] && [[ "$NEW_DB" != "NEEDS CLARIFICATION" ]] && ! grep -q "$NEW_DB" "$target_file"; then
        new_tech_entries+=("- $NEW_DB ($CURRENT_BRANCH)")
    fi
    
    # Подготовить новую запись изменений
    if [[ -n "$tech_stack" ]]; then
        new_change_entry="- $CURRENT_BRANCH: Добавлено $tech_stack"
    elif [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]] && [[ "$NEW_DB" != "NEEDS CLARIFICATION" ]]; then
        new_change_entry="- $CURRENT_BRANCH: Добавлено $NEW_DB"
    fi
    
    # Проверить, существуют ли разделы в файле
    local has_active_technologies=0
    local has_recent_changes=0
    
    if grep -q "^## Active Technologies" "$target_file" 2>/dev/null; then
        has_active_technologies=1
    fi
    
    if grep -q "^## Recent Changes" "$target_file" 2>/dev/null; then
        has_recent_changes=1
    fi
    
    # Обработать файл построчно
    local in_tech_section=false
    local in_changes_section=false
    local tech_entries_added=false
    local changes_entries_added=false
    local existing_changes_count=0
    local file_ended=false
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Обработать раздел "Active Technologies"
        if [[ "$line" == "## Active Technologies" ]]; then
            echo "$line" >> "$temp_file"
            in_tech_section=true
            continue
        elif [[ $in_tech_section == true ]] && [[ "$line" =~ ^##[[:space:]] ]]; then
            # Добавить новые записи технологий перед закрытием раздела
            if [[ $tech_entries_added == false ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
                printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
                tech_entries_added=true
            fi
            echo "$line" >> "$temp_file"
            in_tech_section=false
            continue
        elif [[ $in_tech_section == true ]] && [[ -z "$line" ]]; then
            # Добавить новые записи технологий перед пустой строкой в разделе технологий
            if [[ $tech_entries_added == false ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
                printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
                tech_entries_added=true
            fi
            echo "$line" >> "$temp_file"
            continue
        fi
        
        # Обработать раздел "Recent Changes"
        if [[ "$line" == "## Recent Changes" ]]; then
            echo "$line" >> "$temp_file"
            # Добавить новую запись изменений сразу после заголовка
            if [[ -n "$new_change_entry" ]]; then
                echo "$new_change_entry" >> "$temp_file"
            fi
            in_changes_section=true
            changes_entries_added=true
            continue
        elif [[ $in_changes_section == true ]] && [[ "$line" =~ ^##[[:space:]] ]]; then
            echo "$line" >> "$temp_file"
            in_changes_section=false
            continue
        elif [[ $in_changes_section == true ]] && [[ "$line" == "- "* ]]; then
            # Сохранить только первые 2 существующих изменения
            if [[ $existing_changes_count -lt 2 ]]; then
                echo "$line" >> "$temp_file"
                ((existing_changes_count++))
            fi
            continue
        fi
        
        # Обновить временную метку
        if [[ "$line" =~ \*\*Last\ updated\*\*:.*[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] ]]; then
            echo "$line" | sed "s/[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/$current_date/" >> "$temp_file"
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$target_file"
    
    # Проверка после цикла: если мы все еще в разделе "Active Technologies" и не добавили новые записи
    if [[ $in_tech_section == true ]] && [[ $tech_entries_added == false ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
        printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
        tech_entries_added=true
    fi
    
    # Если разделы не существуют, добавить их в конец файла
    if [[ $has_active_technologies -eq 0 ]] && [[ ${#new_tech_entries[@]} -gt 0 ]]; then
        echo "" >> "$temp_file"
        echo "## Active Technologies" >> "$temp_file"
        printf '%s\n' "${new_tech_entries[@]}" >> "$temp_file"
        tech_entries_added=true
    fi
    
    if [[ $has_recent_changes -eq 0 ]] && [[ -n "$new_change_entry" ]]; then
        echo "" >> "$temp_file"
        echo "## Recent Changes" >> "$temp_file"
        echo "$new_change_entry" >> "$temp_file"
        changes_entries_added=true
    fi
    
    # Атомарно переместить временный файл в целевой
    if ! mv "$temp_file" "$target_file"; then
        log_error "Не удалось обновить целевой файл"
        rm -f "$temp_file"
        return 1
    fi
    
    return 0
}
#==============================================================================
# Основная функция обновления файла агента
#==============================================================================

update_agent_file() {
    local target_file="$1"
    local agent_name="$2"
    
    if [[ -z "$target_file" ]] || [[ -z "$agent_name" ]]; then
        log_error "update_agent_file требует параметры target_file и agent_name"
        return 1
    fi
    
    log_info "Обновление файла контекста $agent_name: $target_file"
    
    local project_name
    project_name=$(basename "$REPO_ROOT")
    local current_date
    current_date=$(date +%Y-%m-%d)
    
    # Создать каталог, если он не существует
    local target_dir
    target_dir=$(dirname "$target_file")
    if [[ ! -d "$target_dir" ]]; then
        if ! mkdir -p "$target_dir"; then
            log_error "Не удалось создать каталог: $target_dir"
            return 1
        fi
    fi
    
    if [[ ! -f "$target_file" ]]; then
        # Создать новый файл из шаблона
        local temp_file
        temp_file=$(mktemp) || {
            log_error "Не удалось создать временный файл"
            return 1
        }
        
        if create_new_agent_file "$target_file" "$temp_file" "$project_name" "$current_date"; then
            if mv "$temp_file" "$target_file"; then
                log_success "Создан новый файл контекста $agent_name"
            else
                log_error "Не удалось переместить временный файл в $target_file"
                rm -f "$temp_file"
                return 1
            fi
        else
            log_error "Не удалось создать новый файл агента"
            rm -f "$temp_file"
            return 1
        fi
    else
        # Обновить существующий файл
        if [[ ! -r "$target_file" ]]; then
            log_error "Невозможно прочитать существующий файл: $target_file"
            return 1
        fi
        
        if [[ ! -w "$target_file" ]]; then
            log_error "Невозможно записать в существующий файл: $target_file"
            return 1
        fi
        
        if update_existing_agent_file "$target_file" "$current_date"; then
            log_success "Обновлен существующий файл контекста $agent_name"
        else
            log_error "Не удалось обновить существующий файл агента"
            return 1
        fi
    fi
    
    return 0
}

#==============================================================================
# Выбор и обработка агента
#==============================================================================

update_specific_agent() {
    local agent_type="$1"
    
    case "$agent_type" in
        claude)
            update_agent_file "$CLAUDE_FILE" "Claude Code"
            ;;
        gemini)
            update_agent_file "$GEMINI_FILE" "Gemini CLI"
            ;;
        copilot)
            update_agent_file "$COPILOT_FILE" "GitHub Copilot"
            ;;
        cursor-agent)
            update_agent_file "$CURSOR_FILE" "Cursor IDE"
            ;;
        qwen)
            update_agent_file "$QWEN_FILE" "Qwen Code"
            ;;
        opencode)
            update_agent_file "$AGENTS_FILE" "opencode"
            ;;
        codex)
            update_agent_file "$AGENTS_FILE" "Codex CLI"
            ;;
        windsurf)
            update_agent_file "$WINDSURF_FILE" "Windsurf"
            ;;
        kilocode)
            update_agent_file "$KILOCODE_FILE" "Kilo Code"
            ;;
        auggie)
            update_agent_file "$AUGGIE_FILE" "Auggie CLI"
            ;;
        roo)
            update_agent_file "$ROO_FILE" "Roo Code"
            ;;
        codebuddy)
            update_agent_file "$CODEBUDDY_FILE" "CodeBuddy CLI"
            ;;
        amp)
            update_agent_file "$AMP_FILE" "Amp"
            ;;
        q)
            update_agent_file "$Q_FILE" "Amazon Q Developer CLI"
            ;;
        *)
            log_error "Неизвестный тип агента '$agent_type'"
            log_error "Ожидается: claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|roo|amp|q"
            exit 1
            ;;
    esac
}

update_all_existing_agents() {
    local found_agent=false
    
    # Проверить каждый возможный файл агента и обновить, если он существует
    if [[ -f "$CLAUDE_FILE" ]]; then
        update_agent_file "$CLAUDE_FILE" "Claude Code"
        found_agent=true
    fi
    
    if [[ -f "$GEMINI_FILE" ]]; then
        update_agent_file "$GEMINI_FILE" "Gemini CLI"
        found_agent=true
    fi
    
    if [[ -f "$COPILOT_FILE" ]]; then
        update_agent_file "$COPILOT_FILE" "GitHub Copilot"
        found_agent=true
    fi
    
    if [[ -f "$CURSOR_FILE" ]]; then
        update_agent_file "$CURSOR_FILE" "Cursor IDE"
        found_agent=true
    fi
    
    if [[ -f "$QWEN_FILE" ]]; then
        update_agent_file "$QWEN_FILE" "Qwen Code"
        found_agent=true
    fi
    
    if [[ -f "$AGENTS_FILE" ]]; then
        update_agent_file "$AGENTS_FILE" "Codex/opencode"
        found_agent=true
    fi
    
    if [[ -f "$WINDSURF_FILE" ]]; then
        update_agent_file "$WINDSURF_FILE" "Windsurf"
        found_agent=true
    fi
    
    if [[ -f "$KILOCODE_FILE" ]]; then
        update_agent_file "$KILOCODE_FILE" "Kilo Code"
        found_agent=true
    fi

    if [[ -f "$AUGGIE_FILE" ]]; then
        update_agent_file "$AUGGIE_FILE" "Auggie CLI"
        found_agent=true
    fi
    
    if [[ -f "$ROO_FILE" ]]; then
        update_agent_file "$ROO_FILE" "Roo Code"
        found_agent=true
    fi

    if [[ -f "$CODEBUDDY_FILE" ]]; then
        update_agent_file "$CODEBUDDY_FILE" "CodeBuddy CLI"
        found_agent=true
    fi

    if [[ -f "$Q_FILE" ]]; then
        update_agent_file "$Q_FILE" "Amazon Q Developer CLI"
        found_agent=true
    fi
    
    # Если файлы агента не существуют, создать файл Claude по умолчанию
    if [[ "$found_agent" == false ]]; then
        log_info "Не найдено существующих файлов агента, создание файла Claude по умолчанию..."
        update_agent_file "$CLAUDE_FILE" "Claude Code"
    fi
}
print_summary() {
    echo
    log_info "Сводка изменений:"
    
    if [[ -n "$NEW_LANG" ]]; then
        echo "  - Добавлен язык: $NEW_LANG"
    fi
    
    if [[ -n "$NEW_FRAMEWORK" ]]; then
        echo "  - Добавлен фреймворк: $NEW_FRAMEWORK"
    fi
    
    if [[ -n "$NEW_DB" ]] && [[ "$NEW_DB" != "N/A" ]]; then
        echo "  - Добавлена база данных: $NEW_DB"
    fi
    
    echo

    log_info "Использование: $0 [claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|codebuddy|q]"
}

#==============================================================================
# Основное выполнение
#==============================================================================

main() {
    # Проверить окружение перед продолжением
    validate_environment
    
    log_info "=== Обновление файлов контекста агента для функции $CURRENT_BRANCH ==="
    
    # Разобрать файл плана для извлечения информации о проекте
    if ! parse_plan_data "$NEW_PLAN"; then
        log_error "Не удалось разобрать данные плана"
        exit 1
    fi
    
    # Обработать в зависимости от аргумента типа агента
    local success=true
    
    if [[ -z "$AGENT_TYPE" ]]; then
        # Не указан конкретный агент - обновить все существующие файлы агента
        log_info "Агент не указан, обновление всех существующих файлов агента..."
        if ! update_all_existing_agents; then
            success=false
        fi
    else
        # Указан конкретный агент - обновить только этого агента
        log_info "Обновление конкретного агента: $AGENT_TYPE"
        if ! update_specific_agent "$AGENT_TYPE"; then
            success=false
        fi
    fi
    
    # Напечатать сводку
    print_summary
    
    if [[ "$success" == true ]]; then
        log_success "Обновление контекста агента завершено успешно"
        exit 0
    else
        log_error "Обновление контекста агента завершено с ошибками"
        exit 1
    fi
}

# Выполнить основную функцию, если скрипт запущен напрямую
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
