#!/usr/bin/env python3
"""
Скрипт для анализа спецификаций в соответствии с командой /speckit.analyze.md

Этот скрипт анализирует файлы spec.md, plan.md, tasks.md и constitution.md (если существует)
на предмет дубликатов, неоднозначностей, несоответствий, недостающих элементов и других проблем.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    """Класс для представления найденной проблемы в спецификациях"""
    id: str
    category: str
    severity: str  # 'Critical', 'High', 'Medium', 'Low'
    location: str # файл и строка
    summary: str
    recommendation: str


@dataclass
class CoverageItem:
    """Класс для представления элемента покрытия"""
    requirement_id: str
    requirement_text: str
    covered_by: List[str] # список задач, покрывающих требование


class SpecAnalyzer:
    """Анализатор спецификаций"""
    
    def __init__(self, spec_dir: str):
        # Используем абсолютный путь к директории спецификации
        self.spec_dir = Path(spec_dir).resolve()
        self.findings: List[Finding] = []
        self.coverage: List[CoverageItem] = []
        
    def load_documents(self) -> Dict[str, str]:
        """Загрузка всех необходимых документов"""
        documents = {}
        
        # Загрузка основных файлов спецификации
        for filename in ['spec.md', 'plan.md', 'tasks.md']:
            file_path = self.spec_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents[filename] = f.read()
            else:
                print(f"Предупреждение: файл {filename} не найден в {self.spec_dir}")
        
        # Также проверим в родительской директории на случай символической ссылки
        parent_dir = self.spec_dir.parent
        for filename in ['spec.md', 'plan.md', 'tasks.md']:
            if filename not in documents:  # если файл еще не загружен
                file_path = parent_dir / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        documents[filename] = f.read()
                else:
                    # Проверим в директории 003-flat-structure-analysis (символическая ссылка)
                    alt_dir = Path("specs/003-flat-structure-analysis")
                    if alt_dir.exists():
                        file_path = alt_dir / filename
                        if file_path.exists():
                            with open(file_path, 'r', encoding='utf-8') as f:
                                documents[filename] = f.read()
                        else:
                            print(f"Предупреждение: файл {filename} не найден в {self.spec_dir}, {parent_dir} и specs/003-flat-structure-analysis")
                    else:
                        print(f"Предупреждение: файл {filename} не найден в {self.spec_dir}, {parent_dir}")
        
        # Загрузка constitution.md, если существует
        constitution_path = Path('specs/constitution.md')
        if constitution_path.exists():
            with open(constitution_path, 'r', encoding='utf-8') as f:
                documents['constitution.md'] = f.read()
        else:
            # Проверим в текущей директории проекта
            constitution_path = Path('specification/constitution.md')
            if constitution_path.exists():
                with open(constitution_path, 'r', encoding='utf-8') as f:
                    documents['constitution.md'] = f.read()
        
        return documents
    
    def analyze_spec(self, content: str, filename: str) -> List[Finding]:
        """Анализ файла спецификации"""
        findings = []
        lines = content.split('\n')
        
        # Проверка на наличие обязательных секций
        content_lower = content.lower()
        
        required_sections = [
            ('## пользовательские сценарии и тестирование', 'spec.md'),
            ('## требования', 'spec.md'),
            ('## критерии успеха', 'spec.md')
        ]
        
        for section, expected_file in required_sections:
            if expected_file in filename.lower() and section not in content_lower:
                findings.append(Finding(
                    id=f"MISSING_SECTION_{len(findings)+1}",
                    category="Структура",
                    severity="High",
                    location=f"{filename}:1",
                    summary=f"Отсутствует обязательная секция: {section}",
                    recommendation=f"Добавьте секцию '{section.upper()}' в файл {filename}"
                ))
        
        # Поиск дубликатов требований
        requirement_pattern = r'((?:FR|NR|PR|SC)-\d+)'
        requirements = re.findall(requirement_pattern, content)
        unique_requirements = set(requirements)
        
        if len(requirements) != len(unique_requirements):
            duplicate_reqs = []
            seen = set()
            for req in requirements:
                if req in seen:
                    if req not in duplicate_reqs:
                        duplicate_reqs.append(req)
                else:
                    seen.add(req)
            
            findings.append(Finding(
                id="DUPLICATE_REQUIREMENTS",
                category="Дубликаты",
                severity="Medium",
                location=f"{filename}:1-{len(lines)}",
                summary=f"Найдены дубликаты требований: {', '.join(duplicate_reqs)}",
                recommendation="Убедитесь, что каждое требование имеет уникальный идентификатор"
            ))
        
        # Поиск неоднозначностей (слишком короткие требования)
        for i, line in enumerate(lines, 1):
            if re.match(requirement_pattern, line.strip()):
                # Проверяем длину строки требования
                if len(line.strip()) < 20:
                    findings.append(Finding(
                        id=f"SHORT_REQUIREMENT_{i}",
                        category="Ясность",
                        severity="Medium",
                        location=f"{filename}:{i}",
                        summary=f"Слишком короткое требование: {line.strip()}",
                        recommendation="Расширьте формулировку требования для лучшего понимания"
                    ))
        
        # Проверка на соответствие конституции (глобальным правилам)
        if 'async/await' in content or 'async def' in content:
            findings.append(Finding(
                id="ASYNC_USAGE",
                category="Конституция",
                severity="Critical",
                location=f"{filename}:1-{len(lines)}",
                summary="Обнаружено использование async/await, что запрещено конституцией",
                recommendation="Удалите все использования async/await и реализуйте синхронную логику"
            ))
        
        return findings
    
    def analyze_plan(self, content: str, filename: str) -> List[Finding]:
        """Анализ файла плана"""
        findings = []
        lines = content.split('\n')
        
        # Проверка на наличие обязательных элементов
        content_lower = content.lower()
        
        required_elements = [
            ('## резюме', 'plan.md'),
            ('## технический контекст', 'plan.md'),
            ('## проверка конституции', 'plan.md'),
            ('## структура проекта', 'plan.md')
        ]
        
        for element, expected_file in required_elements:
            if expected_file in filename.lower() and element not in content_lower:
                findings.append(Finding(
                    id=f"MISSING_ELEMENT_{len(findings)+1}",
                    category="Структура",
                    severity="High",
                    location=f"{filename}:1",
                    summary=f"Отсутствует обязательный элемент: {element}",
                    recommendation=f"Добавьте элемент '{element.upper()}' в файл {filename}"
                ))
        
        # Проверка на соответствие конституции
        if 'async/await' in content:
            findings.append(Finding(
                id="PLAN_ASYNC_USAGE",
                category="Конституция",
                severity="Critical",
                location=f"{filename}:1-{len(lines)}",
                summary="Обнаружено упоминание async/await в плане, что запрещено конституцией",
                recommendation="Удалите все упоминания async/await из плана"
            ))
        
        return findings
    
    def analyze_tasks(self, content: str, filename: str) -> List[Finding]:
        """Анализ файла задач"""
        findings = []
        lines = content.split('\n')
        
        # Проверка формата задач
        task_pattern = r'\[.?\] (T\d+) (\[P\])? (\[US\d+\])? (.+)'
        
        tasks = []
        for i, line in enumerate(lines, 1):
            match = re.match(task_pattern, line.strip())
            if match:
                task_id, parallel, user_story, description = match.groups()
                tasks.append({
                    'id': task_id,
                    'line': i,
                    'parallel': bool(parallel),
                    'user_story': user_story,
                    'description': description
                })
        
        # Проверка на дубликаты задач
        task_ids = [task['id'] for task in tasks]
        unique_task_ids = set(task_ids)
        
        if len(task_ids) != len(unique_task_ids):
            duplicate_tasks = []
            seen = set()
            for task_id in task_ids:
                if task_id in seen:
                    if task_id not in duplicate_tasks:
                        duplicate_tasks.append(task_id)
                else:
                    seen.add(task_id)
            
            findings.append(Finding(
                id="DUPLICATE_TASKS",
                category="Дубликаты",
                severity="High",
                location=f"{filename}:1-{len(lines)}",
                summary=f"Найдены дубликаты задач: {', '.join(duplicate_tasks)}",
                recommendation="Убедитесь, что каждая задача имеет уникальный идентификатор"
            ))
        
        # Проверка на задачи без привязки к пользовательским историям
        tasks_without_story = [task for task in tasks if not task['user_story']]
        if len(tasks_without_story) > 0:
            findings.append(Finding(
                id="TASKS_WITHOUT_STORY",
                category="Трассируемость",
                severity="Medium",
                location=f"{filename}:1-{len(lines)}",
                summary=f"Найдено {len(tasks_without_story)} задач без привязки к пользовательской истории",
                recommendation="Привяжите все задачи к соответствующим пользовательским историям (US1, US2 и т.д.)"
            ))
        
        return findings
    
    def analyze_constitution(self, content: str, filename: str) -> List[Finding]:
        """Анализ файла конституции"""
        findings = []
        
        # В данном проекте конституция встроена в глобальные правила
        # Проверим на соответствие известным правилам
        content_lower = content.lower()
        
        if 'async/await' in content_lower:
            findings.append(Finding(
                id="CONSTITUTION_ASYNC",
                category="Конституция",
                severity="Critical",
                location=f"{filename}:1",
                summary="Конституция содержит разрешение на использование async/await, что противоречит глобальным правилам",
                recommendation="Исправьте конституцию, запретив использование async/await"
            ))
        
        return findings
    
    def analyze_cross_document_consistency(self, documents: Dict[str, str]) -> List[Finding]:
        """Анализ согласованности между документами"""
        findings = []
        
        # Проверка соответствия задач требованиям
        if 'spec.md' in documents and 'tasks.md' in documents:
            spec_content = documents['spec.md']
            tasks_content = documents['tasks.md']
            
            # Извлечение требований из spec
            requirement_pattern = r'(FR|NR|PR|SC)-\d+'
            spec_requirements = re.findall(requirement_pattern, spec_content)
            
            # Извлечение требований из spec.md с использованием более точного паттерна
            spec_req_pattern = r'- \*\*((?:FR|NR|PR|SC)-\d+)\*\*'
            spec_requirements = re.findall(spec_req_pattern, spec_content)
            
            # Если первый подход не сработал, пробуем альтернативный
            if not spec_requirements:
                spec_req_pattern = r'((?:FR|NR|PR|SC)-\d+):'
                spec_requirements = re.findall(spec_req_pattern, spec_content)
            
            # Извлечение упоминаний требований в задачах
            task_requirements = re.findall(r'((?:FR|NR|PR|SC)-\d+)', tasks_content)
            
            # Проверка, что все требования из spec покрыты задачами
            uncovered_requirements = []
            for req in spec_requirements:
                if req not in task_requirements:
                    uncovered_requirements.append(req)
            
            if uncovered_requirements:
                findings.append(Finding(
                    id="UNCOVERED_REQUIREMENTS",
                    category="Трассируемость",
                    severity="High",
                    location="spec.md, tasks.md",
                    summary=f"Непокрытые требования из spec.md в задачах: {', '.join(uncovered_requirements)}",
                    recommendation="Добавьте задачи, покрывающие все функциональные и нефункциональные требования"
                ))
        
        # Проверка согласования пользовательских историй
        if 'spec.md' in documents and 'tasks.md' in documents:
            spec_content = documents['spec.md']
            tasks_content = documents['tasks.md']
            
            # Извлечение пользовательских историй из spec
            us_pattern = r'### Пользовательская история (\d+)'
            spec_user_stories = re.findall(us_pattern, spec_content)
            
            # Извлечение упоминаний пользовательских историй в задачах
            task_user_stories = re.findall(r'\[US(\d+)\]', tasks_content)
            
            # Проверка соответствия
            for us in spec_user_stories:
                if us not in task_user_stories:
                    findings.append(Finding(
                        id=f"UNMAPPED_USER_STORY_{us}",
                        category="Трассируемость",
                        severity="Medium",
                        location="spec.md, tasks.md",
                        summary=f"Пользовательская история US{us} из spec.md не имеет задач в tasks.md",
                        recommendation=f"Добавьте задачи для пользовательской истории US{us}"
                    ))
        
        return findings
    
    def generate_coverage_report(self, documents: Dict[str, str]) -> List[CoverageItem]:
        """Генерация отчета о покрытии требований задачами"""
        coverage = []
        
        if 'spec.md' in documents and 'tasks.md' in documents:
            spec_content = documents['spec.md']
            tasks_content = documents['tasks.md']
            
            # Используем более точный паттерн для извлечения требований
            # Ищем строки вида "- **FR-001**: Текст требования"
            requirement_pattern = r'- \*\*(?P<id>(?:FR|NR|PR|SC)-\d+)\*\*:\s*(?P<text>.*?)(?=\n\s*- \*\*|\n\s*##|\Z)'
            matches = re.finditer(requirement_pattern, spec_content, re.MULTILINE | re.DOTALL)
            
            requirements = []
            for match in matches:
                req_id = match.group('id')
                req_text = match.group('text').strip()
                requirements.append((req_id, req_text))
            
            # Если первый подход не сработал, пробуем альтернативный
            if not requirements:
                requirement_pattern = r'((?:FR|NR|PR|SC)-\d+):\s*(.*?)(?:\n|$)'
                requirements = re.findall(requirement_pattern, spec_content)
            
            for req_id, req_text in requirements:
                # Найти задачи, упоминающие это требование
                covered_tasks = re.findall(r'\[.?\] (T\d+).*?' + re.escape(req_id), tasks_content, re.IGNORECASE)
                
                coverage.append(CoverageItem(
                    requirement_id=req_id,
                    requirement_text=req_text.strip(),
                    covered_by=covered_tasks
                ))
        
        return coverage
    
    def analyze(self) -> Tuple[List[Finding], List[CoverageItem]]:
        """Основной метод анализа всех документов"""
        documents = self.load_documents()
        
        # Очистка предыдущих результатов
        self.findings = []
        self.coverage = []
        
        # Анализ каждого документа
        for filename, content in documents.items():
            if filename == 'spec.md':
                self.findings.extend(self.analyze_spec(content, filename))
            elif filename == 'plan.md':
                self.findings.extend(self.analyze_plan(content, filename))
            elif filename == 'tasks.md':
                self.findings.extend(self.analyze_tasks(content, filename))
            elif filename == 'constitution.md':
                self.findings.extend(self.analyze_constitution(content, filename))
        
        # Анализ согласованности между документами
        self.findings.extend(self.analyze_cross_document_consistency(documents))
        
        # Генерация отчета о покрытии
        self.coverage = self.generate_coverage_report(documents)
        
        return self.findings, self.coverage


def format_findings_table(findings: List[Finding]) -> str:
    """Форматирование таблицы с найденными проблемами"""
    if not findings:
        return "Нет найденных проблем"
    
    table = "| ID | Категория | Серьезность | Местоположение | Сводка | Рекомендация |\n"
    table += "|---|---|---|---|---|---|\n"
    
    for finding in findings:
        table += f"| {finding.id} | {finding.category} | {finding.severity} | {finding.location} | {finding.summary} | {finding.recommendation} |\n"
    
    return table


def format_coverage_table(coverage: List[CoverageItem]) -> str:
    """Форматирование таблицы покрытия"""
    if not coverage:
        return "Нет данных о покрытии"
    
    table = "| ID Требования | Текст требования | Покрыто задачами |\n"
    table += "|---|---|---|\n"
    
    for item in coverage:
        covered_by = ', '.join(item.covered_by) if item.covered_by else "Не покрыто"
        table += f"| {item.requirement_id} | {item.requirement_text} | {covered_by} |\n"
    
    return table


def format_constitution_issues(findings: List[Finding]) -> str:
    """Форматирование сводки по несоответствиям конституции"""
    constitution_findings = [f for f in findings if f.category == "Конституция"]
    
    if not constitution_findings:
        return "Нет несоответствий конституции"
    
    result = "### Несоответствия конституции:\n\n"
    for finding in constitution_findings:
        result += f"- **{finding.severity}**: {finding.summary} ({finding.location})\n"
    
    return result


def format_unmapped_tasks(documents: Dict[str, str]) -> str:
    """Форматирование списка задач без сопоставления"""
    if 'tasks.md' not in documents:
        return "Файл задач не найден"
    
    tasks_content = documents['tasks.md']
    task_pattern = r'\[.?\] (T\d+) (\[P\])? (\[US\d+\])? (.+)'
    
    unmapped_tasks = []
    for line_num, line in enumerate(tasks_content.split('\n'), 1):
        match = re.match(task_pattern, line.strip())
        if match:
            task_id, parallel, user_story, description = match.groups()
            if not user_story:  # Задача не привязана к пользовательской истории
                unmapped_tasks.append(f"  - {task_id} на строке {line_num}: {description}")
    
    if not unmapped_tasks:
        return "Нет задач без сопоставления"
    
    return "### Задачи без сопоставления с пользовательскими историями:\n\n" + "\n".join(unmapped_tasks)


def calculate_metrics(findings: List[Finding], coverage: List[CoverageItem]) -> str:
    """Расчет метрик анализа"""
    total_findings = len(findings)
    critical_findings = len([f for f in findings if f.severity == "Critical"])
    high_findings = len([f for f in findings if f.severity == "High"])
    medium_findings = len([f for f in findings if f.severity == "Medium"])
    low_findings = len([f for f in findings if f.severity == "Low"])
    
    total_requirements = len(coverage)
    covered_requirements = len([c for c in coverage if c.covered_by])
    uncovered_requirements = total_requirements - covered_requirements
    
    coverage_percentage = (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0
    
    metrics = f"""
### Метрики:
- Всего найдено проблем: {total_findings}
  - Критические: {critical_findings}
  - Высокий приоритет: {high_findings}
  - Средний приоритет: {medium_findings}
  - Низкий приоритет: {low_findings}
- Покрытие требований: {covered_requirements}/{total_requirements} ({coverage_percentage:.1f}%)
- Непокрытые требования: {uncovered_requirements}
"""
    
    return metrics


def main():
    """Основная функция"""
    spec_dir = "specs/03-flat-structure"
    analyzer = SpecAnalyzer(spec_dir)
    
    findings, coverage = analyzer.analyze()
    
    # Загрузка документов для форматирования отчета
    documents = analyzer.load_documents()
    
    # Формирование отчета
    report = "# Отчет об анализе спецификаций\n\n"
    report += "## Таблица найденных проблем\n\n"
    report += format_findings_table(findings) + "\n\n"
    
    report += "## Таблица покрытия требований\n\n"
    report += format_coverage_table(coverage) + "\n\n"
    
    report += "## Сводка по несоответствиям конституции\n\n"
    report += format_constitution_issues(findings) + "\n\n"
    
    report += "## Задачи без сопоставления\n"
    report += format_unmapped_tasks(documents) + "\n\n"
    
    report += calculate_metrics(findings, coverage)
    
    report += """
## Рекомендации по следующим действиям:
1. Исправить все критические и высокоприоритетные проблемы
2. Обеспечить полное покрытие всех требований задачами
3. Привязать все задачи к соответствующим пользовательским историям
4. Проверить соответствие всему содержанию конституции проекта
5. Обновить документацию после внесения изменений
"""
    
    # Сохранение отчета
    output_path = Path(spec_dir) / "analysis_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Отчет об анализе сохранен в {output_path}")
    print(f"Найдено {len(findings)} проблем")
    print(f"Проанализировано {len(coverage)} требований")


if __name__ == "__main__":
    main()