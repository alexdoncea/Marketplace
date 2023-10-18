"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import unittest
from threading import Lock
import logging
import time
from logging.handlers import RotatingFileHandler
from .product import Product


LOGGER = logging.getLogger('Test marketplace methods')
LOGGER.setLevel(logging.DEBUG)

FILEHANDLER = RotatingFileHandler('marketplace.log', maxBytes=100000, backupCount=5)
FILEHANDLER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
FORMATTER.converter = time.gmtime

FILEHANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILEHANDLER)

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        LOGGER.info("Called constructor")
        self.size = queue_size_per_producer
        self.queue_size = {}
        self.queue_prod = []
        self.carts = {}
        self.producers = 0
        self.cart = 0
        self.lock_producers = Lock()
        self.lock_carts = Lock()
        self.lock_products = Lock()

    def register_producer(self):
        """
        Assigns a unique id to the caller as a producer.
        """
        LOGGER.info("Registering new producer")

        # fac un lock pe producers pentru a nu se suprapune id-urile
        with self.lock_producers:
            # incrementez numarul de producatori si ii atribui un id unic
            self.producers += 1
            self.queue_size[self.producers] = 0
            producer_id = self.producers
        LOGGER.info("Producer %d registered", producer_id)
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        LOGGER.info("Called publish")
        # verific daca producatorul are deja un id
        if producer_id not in self.queue_size:
            self.queue_size[producer_id] = 0

        # verific daca coada producatorului este plina
        if self.queue_size.get(producer_id, 0) >= self.size:
            LOGGER.info("Exit publish with False")
            return False

        # daca nu este plina, adaug produsul in coada
        with self.lock_products:
            self.queue_prod.append([producer_id, product])
            self.queue_size[producer_id] += 1

        LOGGER.info("Exit publish with True")
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        LOGGER.info("create_new_cart called")
        # fac un lock pe carts pentru a nu se suprapune id-urile
        with self.lock_carts:
            self.cart += 1
            self.carts[self.cart] = []
            cart_id = self.cart
            LOGGER.info("create_new_cart completed with cart_id %d", self.cart)
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        LOGGER.info("Called add_product_to_cart")

        with self.lock_products:
            # verific daca produsul exista in coada
            for i, (pid, prod) in enumerate(self.queue_prod):
                if prod == product:
                    # daca exista, il adaug in cos si il sterg din coada
                    self.carts[cart_id].append((pid, prod))
                    del self.queue_prod[i]
                    self.queue_size[pid] -= 1
                    LOGGER.info("Exit add_product_to_cart with True")
                    return True

        LOGGER.info("Exit add_product_to_cart with False")
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        LOGGER.info("remove_product_from_cart called.")

        with self.lock_products:
            # verific daca produsul exista in cos
            for cart_item in self.carts[cart_id]:
                if cart_item[1] == product:
                    # daca exista, il sterg din cos si il adaug in coada
                    self.carts[cart_id].remove(cart_item)
                    self.queue_prod.append(cart_item)
                    self.queue_size[cart_item[0]] += 1
                    break

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        LOGGER.info("Starting place_order")
        # fac un lock pe products pentru a nu se suprapune id-urile
        with self.lock_products:
            # iau toate produsele din cos
            cart_items = self.carts.pop(cart_id, [])
            # le adaug in coada
            products_list = [item[1] for item in cart_items]

        LOGGER.info("Exiting place_order with %s", str(products_list))
        return products_list


class TestMarketplace(unittest.TestCase):
    """
    Unitesting class for class Marketplace
    """
    def setUp(self):
        """
        Method to setup variables for testing
        """
        self.market1 = Marketplace(1)
        self.market2 = Marketplace(3)

    def test_register_producer(self):
        """
        Method to test register_producer method from Marketplace class
        """
        self.assertEqual(self.market1.register_producer(), 1)
        self.assertNotEqual(self.market2.register_producer(), 2)
        self.assertNotEqual(self.market2.register_producer(), 0)

    def test_publish(self):
        """
        Method to test publish method from Marketplace class
        """
        self.market1.register_producer()
        self.market1.register_producer()
        self.assertTrue(self.market1.publish(1, Product.Tea("Linden", 9, "Herbal")))
        self.assertIn([1, Product.Tea("Linden", 9, "Herbal")], self.market1.queue_prod)
        self.market1.publish(2, Product.Tea("Linden", 9, "Herbal"))
        self.assertFalse(self.market1.publish(2, Product.Tea("Linden", 9, "Herbal")))

    def test_new_cart(self):
        """
        Method to test new_cart method from Marketplace class
        """
        self.assertEqual(self.market1.new_cart(), 1)
        self.assertNotEqual(self.market1.new_cart(), 3)
        self.assertEqual(self.market2.new_cart(), 1)
        self.assertNotEqual(self.market2.new_cart(), 1)

    def test_add_to_cart(self):
        """
        Method to test add_to_cart method from Marketplace class
        """
        self.market1.register_producer()
        self.market1.register_producer()
        self.market1.new_cart()
        self.market1.publish(1, Product.Tea("Linden", 9, "Herbal"))
        self.market1.publish(2, Product.Tea("Linden", 9, "Herbal"))
        self.assertTrue(self.market1.add_to_cart(1, Product.Tea("Linden", 9, "Herbal")))
        self.assertTrue(self.market1.add_to_cart(1, Product.Tea("Linden", 9, "Herbal")))
        self.assertFalse(self.market1.add_to_cart(1, Product.Tea("Linden", 9, "Herbal")))
        self.assertIn(
            Product.Tea("Linden", 9, "Herbal"), map(lambda p: p[1], self.market1.carts[1]))
        self.assertNotIn(
            Product.Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM'),
            map(lambda p: p[1], self.market1.carts[1]))

    def test_remove_from_cart(self):
        """
        Method to test remove_from_cart method from Marketplace class
        """
        self.market1.register_producer()
        self.market1.register_producer()
        self.market1.new_cart()
        self.market1.publish(1, Product.Tea("Linden", 9, "Herbal"))
        self.market1.publish(2, Product.Tea("Linden", 9, "Herbal"))
        self.market1.add_to_cart(1, Product.Tea("Linden", 9, "Herbal"))
        self.market1.add_to_cart(1, Product.Tea("Linden", 9, "Herbal"))
        self.market1.remove_from_cart(1, Product.Tea("Linden", 9, "Herbal"))
        self.assertEqual(1, len(self.market1.carts[1]))
        self.assertIn([2, Product.Tea("Linden", 9, "Herbal")], self.market1.carts[1])

    def test_place_order(self):
        """
        Method to test place_order method from Marketplace class
        """
        self.market2.register_producer()
        self.market2.register_producer()
        self.market2.new_cart()
        self.market2.publish(1, Product.Tea("Linden", 9, "Herbal"))
        self.market2.publish(2, Product.Tea("Linden", 9, "Herbal"))
        self.market2.publish(
            1, Product.Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM'))
        self.market2.add_to_cart(1, Product.Tea("Linden", 9, "Herbal"))
        self.market2.add_to_cart(
            1, Product.Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM'))
        self.market2.add_to_cart(1, Product.Tea("Linden", 9, "Herbal"))
        self.market2.remove_from_cart(1, Product.Tea("Linden", 9, "Herbal"))
        self.assertEqual(
            [Product.Coffee(name='Indonezia', price=1, acidity=5.05, roast_level='MEDIUM'),
             Product.Tea("Linden", 9, "Herbal")], self.market2.place_order(1))
        self.assertFalse(1 in self.market2.carts)
