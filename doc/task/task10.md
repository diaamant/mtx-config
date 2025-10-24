# План дальнейшего развития Mediamtx Configuration Editor

**Дата:** 2025-10-24
**Версия:** 0.2.1 (обновлено с учетом анализа)


## 1. Высокий приоритет (P1)



### 1.2. Функционал: Импорт и Экспорт
- **Задача:** Реализовать экспорт и импорт конфигурации.
- **Обоснование:** Позволяет пользователям делиться конфигурациями, создавать резервные копии и переносить настройки между серверами.
- **Реализация:**
    - Добавить кнопки "Экспорт" и "Импорт" в хедер.
    - **Экспорт:** Собирает текущую конфигурацию в `mediamtx.yml` и предлагает скачать файл.
    - **Импорт:** Позволяет загрузить `mediamtx.yml`, парсит его и обновляет данные в `MtxConfigManager` с последующим обновлением UI.
    - **Валидация:** При импорте использовать Pydantic-модели для строгой проверки корректности структуры и типов данных загружаемого файла.

    Plan Update

   1. Modify `main.py`:
       * Add "Import" and "Export" buttons to the ui.header.
       * The "Export" button will call a new export_config method in MtxConfigManager.
       * The "Import" button will use ui.upload to get a file and then call a new import_config method in MtxConfigManager.

   2. Modify `mtx_manager.py`:
       * Create an export_config method. This will be similar to update_preview but will return the YAML string instead of updating a local variable.
       * Create an import_config method. This method will:
           * Take the YAML content as a string.
           * Use yaml.safe_load to parse it.
           * Crucially, it needs to deconstruct the single YAML file back into the multiple dictionary structures that the application uses (e.g., `paths.json`,
              `values_rtsp.json`, etc.). This is the reverse of what update_preview and save_data do.
           * Validate the imported data against the Pydantic models.
           * If valid, replace the contents of self.data.
           * It must then trigger a UI refresh. This is a critical step. Since the UI is built dynamically, I'll need a way to tell the UI to completely rebuild
              itself. A simple page reload (ui.open('/')) might be the easiest way to ensure all components reflect the new state.

   3. Modify `clients/yaml_client.py` and `clients/json_client.py`:
       * I will need to add a new method to YAMLClient to parse the imported YAML file.
       * I will also need to add a new method to JSONClient to save the imported data to the respective JSON files.


