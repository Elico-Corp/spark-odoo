# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2014 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Augustin Cisterne-Kaas
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp.tests.common as common


class test_category_manager(common.TransactionCase):
    def setUp(self):
        super(test_category_manager, self).setUp()
        self.wizard_pool = self.registry('wizard.category.manager')
        self.product_pool = self.registry('product.product')
        data_pool = self.registry('ir.model.data')
        ''' Get categories demo data '''
        self.category_id_1 = data_pool.get_object_reference(
            self.cr, self.uid, 'product', 'product_category_1')[1]
        self.category_id_2 = data_pool.get_object_reference(
            self.cr, self.uid, 'product', 'product_category_2')[1]
        ''' Get products demo data '''
        self.product_id_1 = data_pool.get_object_reference(
            self.cr, self.uid, 'product', 'product_product_1')[1]
        self.product_id_2 = data_pool.get_object_reference(
            self.cr, self.uid, 'product', 'product_product_2')[1]

    def wizard(self, data):
        wizard_id = self.wizard_pool.create(
            self.cr, self.uid, data)
        return self.wizard_pool.browse(
            self.cr, self.uid, wizard_id)

    def test_01(self):
        ''' Check that the category destination is added to the products '''
        product_1 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_1)
        product_2 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_2)
        self.assertEqual(product_1.categ_ids, [])
        self.assertEqual(product_2.categ_ids, [])
        data = {
            'categ_to': self.category_id_1
        }
        context = {'active_ids': [product_1.id, product_2.id]}
        wizard = self.wizard(data)
        wizard.assign(context=context)
        product_1 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_1)
        product_2 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_2)
        self.assertEqual(product_1.categ_ids[0].id, self.category_id_1)
        self.assertEqual(product_2.categ_ids[0].id, self.category_id_1)

    def test_02(self):
        ''' Check that the category origin is removed from the products '''
        self.test_01()
        data = {
            'categ_from': self.category_id_1
        }
        context = {'active_ids': [self.product_id_1, self.product_id_2]}
        wizard = self.wizard(data)
        wizard.assign(context=context)
        product_1 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_1)
        product_2 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_2)
        self.assertEqual(product_1.categ_ids, [])
        self.assertEqual(product_2.categ_ids, [])

    def test_03(self):
        ''' Check that the category origin is not added to the products
            If category destination does not exist in the product'''
        data = {
            'categ_to': self.category_id_1
        }
        context = {'active_ids': [self.product_id_1]}
        wizard = self.wizard(data)
        wizard.assign(context=context)
        product_1 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_1)
        self.assertEqual(len(product_1.categ_ids), 1)
        self.assertEqual(product_1.categ_ids[0].id, self.category_id_1)
        data = {
            'categ_from': self.category_id_1,
            'categ_to': self.category_id_2
        }
        context = {'active_ids': [self.product_id_1, self.product_id_2]}
        wizard = self.wizard(data)
        wizard.assign(context=context)
        product_1 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_1)
        product_2 = self.product_pool.browse(
            self.cr, self.uid, self.product_id_2)
        self.assertEqual(len(product_1.categ_ids), 1)
        self.assertEqual(product_1.categ_ids[0].id, self.category_id_2)
        self.assertEqual(product_2.categ_ids, [])
