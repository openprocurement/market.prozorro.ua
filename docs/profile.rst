Інструкція Profile
====================

Дістати список **Profiles**.

.. include:: source/responses/listing_profile.http
    :code:

Створення Profile
---------------------

1. Створити **Criteria**.
2. Дістати ``id`` щойно створеної **Criteria** -- ``relatedCriteria_id``
3. Сформувати дані для **Profile**. Параметр **Criteria** в даних для
   **Profile** повинен виглядати ось так:

.. code:: json

    {"criteria": [
       {
         "title": "Test criteria",
         "description": "Test description",
         "requirementGroups": [
           {
             "description": "Test requirement group",
             "requirements": [
               {
                 "title": "Test requirement",
                 "description": "Test requirement description",
                 "relatedCriteria_id": "b8741a7de9cd4fd089987a0a5e4894cc",
                 "expectedValue": "5"
               }
             ]
           }
         ]
       }
     ]}

4. Після створення **Criteria**, у відповіді буде блок ``access``,
   необхідний для можливості редагувати **Profile**.

.. include:: source/responses/create_profile.http
    :code:

Перегляд Profile
--------------------

Редагування Profile
-----------------------

Для редагування **Profile**, крім бажаних даних, потрібно передати
``access`` блок, котрий був отриманий при створенні **Criteria**:

.. code:: json

    {"access": {
       "token": "207b8488df9e455e9a05d6d1e0ffae27",
       "owner": "admin"
     }}

1. Редагування всіх полів, крім **Criteria**.

.. include:: source/responses/patch_profile_title.http
  :code:

2. Редагування поля **Criteria**:

-  Повна заміна поля **Criteria**. Щоб замінити повністю поле
   **Criteria** на нове, потрібно передати новий список **Criteria**
   (такого ж вигляду, як і при створенні):

.. code:: json

    {"criteria": [
         {
           "title": "New criteria",
           "description": "New description",
           "requirementGroups": [
             {
               "description": "New requirement group",
               "requirements": [
                 {
                   "title": "New requirement",
                   "description": "New requirement description",
                   "relatedCriteria_id": "7002e4def5284ff3b2d84625bc4d9012",
                   "expectedValue": "5"
                 }
               ]
             }
           ]
         }
       ]}

.. include:: source/responses/patch_profile_change_criteria_list.http
    :code:

-  Додавання нової **Criteria** до вже існуючих. Щоб додати нову
   **Criteria**, потрібно в поле **Criteria** передати список існуючих у
   вигляді:

.. code:: json

    {
       "id": "5d2f4a2d6d29489da4e59793f7c3a8f1"
    }

Також потрібно додати дані для нової **Criteria** (як згадано вище).

.. include:: source/responses/patch_profile_add_criteria.http
    :code:

-  Редагування **Criteria** (1). Щоб редагувати якусь конкретну
   **Criteria** зі списку, потрібно передати її ``id`` разом з даними
   для редагування:

.. code:: json

    {"criteria": [
         {
           "id": "c58d5f8903c3400bb75020477aab4346",
           "title": "Completely new title"
         },
         {
            "id": "5d2f4a2d6d29489da4e59793f7c3a8f1"
         },
    ]}

Не забуваємо, якщо є інші **Criteria**, котрі ми не хочемо редагувати,
але хочемо залишити, то їх потрібно також передати так, як було описано
вище:

.. code:: json

    {
       "id": "5d2f4a2d6d29489da4e59793f7c3a8f1"
    }

.. include:: source/responses/patch_profile_edit_criteria.http
    :code:

-  Редагування **Criteria** (2). Додавання/заміна/редагування
   ``requirementGroups`` в **Criteria** відбувається аналогічно до
   редагування **Criteria** в **Profile**. Тобто, щоб замінити
   ``requirementGroups``, потрбіно передати список з даними для них:

.. code:: json

    {"criteria": [
         {
           "id": "c58d5f8903c3400bb75020477aab4346",
           "requirementGroups": [
             {
               "description": "Second requirement group",
               "requirements": [
                 {
                   "title": "Second requirement",
                   "description": "Second requirement description",
                   "relatedCriteria_id": "78deb72bd3eb4941a0741ba9466c7e34",
                   "expectedValue": "5"
                 }
               ]
             }
           ]
         }
       ]}

.. include:: source/responses/patch_profile_set_requirement_groups_to_criteria.http
    :code:

Щоб додати нову ``requirementGroup``, потрібно до списку з існуючих
``requirementGroups``, добавити дані для нової:

.. code:: json

    {"criteria": [
         {
           "id": "c58d5f8903c3400bb75020477aab4346",
           "requirementGroups": [
             {
               "id": "2239aa3f0cf644bea7dd58deb551bf17"
             },
             {
               "description": "Second requirement group",
               "requirements": [
                 {
                   "title": "Second requirement",
                   "description": "Second requirement description",
                   "relatedCriteria_id": "78deb72bd3eb4941a0741ba9466c7e34",
                   "expectedValue": "5"
                 }
               ]
             }
           ]
         }]}

.. include:: source/responses/patch_profile_add_requirement_group_to_criteria.http
    :code:

Щоб редагувати ``requirementGroup`` потрібно, разом з даними для
редагування передати ``id`` групи, котру ми хочемо редагувати.

.. code:: json

    {"criteria": [
         {
           "id": "c58d5f8903c3400bb75020477aab4346",
           "requirementGroups": [
             {
               "id": "a9e2d659df3a484bafed0719323b5246",
               "requirements": [
                 {
                   "title": "Requirement 1",
                   "description": "Requirement description 1",
                   "relatedCriteria_id": "78deb72bd3eb4941a0741ba9466c7e34",
                   "expectedValue": "5"
                 },
                 {
                   "title": "Requirement 2",
                   "description": "Requirement description 2",
                   "relatedCriteria_id": "78deb72bd3eb4941a0741ba9466c7e34",
                   "expectedValue": "5"
                 }
               ]
             }
           ]
         }
       ]}

.. include:: source/responses/patch_profile_set_requirements_to_criteria.http
    :code:

Видалення Profile
---------------------

Після видалення **Profile**, він переходить в статус hidden.

.. include:: source/responses/delete_profile.http
    :code:

Фільтрація списку Profile
-----------------------------

Щоб профільтрувати список **Profile** по ``relatedCriteria_id``,
потрібно в GET параметри передати наступні дані:

.. code::

    /api/0/profiles/?criteria_requirementGroups_requirements_relatedCriteria_id=78deb72bd3eb4941a0741ba9466c7e34

.. include:: source/responses/filtering_profile.http
    :code: