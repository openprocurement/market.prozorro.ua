.. _tutorial:

Tutorial
========

Creating Criteria
-----------------

Let's create **Criteria** with the minimal (only required) data set:

.. include:: source/responses/create_criteria.http
   :code:

Success! Now we can see that the new object was created. Response code is `201`
and `Location` response header reports the location of the created object.  The
body of response reveals the information about the created **Criteria**.

Viewing Criteria
----------------

Now let's view **Criteria**.

.. include:: source/responses/view_criteria.http
   :code:

Success! Response code is `200 OK` and the body of response reveals the information about the created **Criteria**.

Modifying Criteria
------------------

Let’s update **Criteria** by supplementing it with all other essential properties:

.. include:: source/responses/patch_criteria.http
   :code:

We see the added properties have merged with existing **Criteria** data.

Deleting Criteria
-----------------

Let's put **Criteria** in the archive, by changing its status to `retire`.

.. include:: source/responses/delete_criteria.http
   :code:

Success! Response code is `204 No Content`. 