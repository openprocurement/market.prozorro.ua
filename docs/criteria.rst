.. _criteria:

Інструкція Criteria
===================

Створення Criteria
------------------

Створити **Criteria** із мінімальним (необхідним) набором даних:

.. include:: source/responses/create_criteria.http
   :code:

Успіх! Як ми бачимо, було створено новий обєкт. Код відповіді є `201`
і `Location` хедер відповіді говорить про місцезнаходження створеного обєкта.
Тіло відповіді показує інформацію про створений обєкт **Criteria**.

Перегляд Criteria
-----------------

Переглянемо **Criteria**.

.. include:: source/responses/view_criteria.http
   :code:

Успіх! Код відповіді є `200 OK` і відповіді показує інформацію про створений обєкт **Criteria**.

Редагування Criteria
--------------------

Відредагуємо **Criteria** шляхом додавання інших параметрів:

.. include:: source/responses/patch_criteria.http
   :code:

Ми бачимо, що передані параметри були додані до існуючих в **Criteria**.

Видалення Criteria
------------------

Перенесемо **Criteria** в архів, за допомогою зміни статусу на `retire`.

.. include:: source/responses/delete_criteria.http
   :code:

Успіх! Код відповіді є `204 No Content`. 