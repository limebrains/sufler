======================
Creation of completion
======================

For example, we want to add completion for command **Food**, so we need to add his arguments in nodes after **:**.

.. code::

    'food': &food
        'fruit': &fruit
            'orange': *fruit
            'banana': *fruit
            'strawberry': *fruit
            'grape':
                'green':
                'red':
            'grapefruit':
                '"ruby red"':
                'yellow':
            '--seedless=': &seedless
                'true': *food
                'false': *food

            '<Exec> ls':
              'rm':

.. note:: All name of nodes need to be in **'**

.. note:: After add last elements in complete tree, just leave **":"** after last node

.. note:: We can add reference to any node of tree. E.g. if we want to repeat completions from **'fruit'** after **'orange'**, between node and subnodes of fruit add anchor **'&'** with name of reference **'&fruit'**. When we have anchor just add reference **'*'** to food **'*food'**.
