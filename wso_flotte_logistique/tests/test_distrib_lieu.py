# -*- coding: utf-8 -*-
'''
Created on 13 juil. 2017

@author: Antsa
'''
from odoo.tests.common import TransactionCase


class Test(TransactionCase):


    def test_find_lieu(self):
        "Find a place by its lon and lat"
        Todo = self.enb['']
        task = Todo.create({'name': 'Test Task'})
        self.assertEqual(task.isdone, False)