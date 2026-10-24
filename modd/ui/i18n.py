from PySide6.QtCore import QObject, Signal

STRINGS = {
    "window.title": {
        "en": "Modd — Mod Development Toolkit",
        "ru": "Modd — инструментарий разработки модов",
    },
    "action.create_project": {"en": "Create Project", "ru": "Создать проект"},
    "action.open_project": {"en": "Open Project", "ru": "Открыть проект"},
    "action.run": {"en": "Run", "ru": "Запустить"},
    "action.debug": {"en": "Debug", "ru": "Отладка"},
    "action.build": {"en": "Build", "ru": "Сборка"},
    "action.deploy": {"en": "Deploy", "ru": "Установить"},
    "action.stop": {"en": "Stop", "ru": "Остановить"},
    "panel.project": {"en": "Project", "ru": "Проект"},
    "panel.problems": {"en": "Problems", "ru": "Проблемы"},
    "panel.console": {"en": "Console", "ru": "Консоль"},
    "panel.debugger": {"en": "Debugger", "ru": "Отладчик"},
    "panel.stack": {"en": "Call Stack", "ru": "Стек вызовов"},
    "panel.variables": {"en": "Variables", "ru": "Переменные"},
    "col.file": {"en": "File", "ru": "Файл"},
    "col.line": {"en": "Line", "ru": "Строка"},
    "col.message": {"en": "Message", "ru": "Сообщение"},
    "col.function": {"en": "Function", "ru": "Функция"},
    "col.name": {"en": "Name", "ru": "Имя"},
    "col.value": {"en": "Value", "ru": "Значение"},
    "debug.step_over": {"en": "Step Over", "ru": "Шаг через"},
    "debug.step_into": {"en": "Step Into", "ru": "Шаг внутрь"},
    "debug.step_out": {"en": "Step Out", "ru": "Из функции"},
    "debug.continue": {"en": "Continue", "ru": "Продолжить"},
    "form.title": {"en": "New Project", "ru": "Новый проект"},
    "form.name": {"en": "Project name", "ru": "Название проекта"},
    "form.game": {"en": "Target game", "ru": "Целевая игра"},
    "form.folder": {"en": "Folder", "ru": "Папка"},
    "form.browse": {"en": "Browse", "ru": "Обзор"},
    "form.create": {"en": "Create", "ru": "Создать"},
    "form.back": {"en": "Back", "ru": "Назад"},
    "status.running": {"en": "Running: {file}", "ru": "Выполняется: {file}"},
    "status.paused": {"en": "Paused: {file}, line {line}", "ru": "Пауза: {file}, строка {line}"},
    "status.finished": {"en": "Finished with exit code {code}", "ru": "Завершено с кодом {code}"},
    "status.saved": {"en": "Saved: {file}", "ru": "Сохранено: {file}"},
    "status.project_opened": {"en": "Project opened: {path}", "ru": "Проект открыт: {path}"},
    "status.no_project": {"en": "Open or create a project first", "ru": "Сначала откройте или создайте проект"},
    "status.no_python_file": {"en": "Open a Python file first", "ru": "Откройте Python-файл"},
    "status.no_adapter": {"en": "No adapter detected for {path}", "ru": "Адаптер для {path} не найден"},
    "status.adapter": {"en": "Adapter: {adapter}", "ru": "Адаптер: {adapter}"},
    "status.build_started": {"en": "Building: {name}", "ru": "Сборка: {name}"},
    "status.deploy_started": {"en": "Deploying: {name}", "ru": "Установка: {name}"},
    "status.build_done": {"en": "Build finished: {path}", "ru": "Сборка завершена: {path}"},
    "status.deploy_done": {"en": "Deploy finished: {path}", "ru": "Установка завершена: {path}"},
    "status.invalid_name": {"en": "Enter a valid project name", "ru": "Укажите корректное название проекта"},
    "status.invalid_folder": {"en": "Choose an existing folder", "ru": "Выберите существующую папку"},
    "status.unsupported_file": {"en": "Unsupported file type", "ru": "Неподдерживаемый тип файла"},
    "problems.unavailable": {
        "en": "{title}: {method} is not available without the game toolchain",
        "ru": "{title}: {method} недоступно без инструментария игры",
    },
    "console.clear": {"en": "Clear", "ru": "Очистить"},
}

LANGUAGES = ("en", "ru")


class I18n(QObject):
    language_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._language = "en"

    def language(self):
        return self._language

    def set_language(self, language):
        if language not in LANGUAGES:
            raise ValueError(language)
        if language == self._language:
            return
        self._language = language
        self.language_changed.emit()

    def tr(self, key, **kwargs):
        text = STRINGS[key][self._language]
        if kwargs:
            text = text.format(**kwargs)
        return text
