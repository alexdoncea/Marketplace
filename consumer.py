"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self)
        self.name = kwargs["name"]
        self.carts = carts
        self.marketplace = marketplace
        self.retry_time = retry_wait_time

    def run(self):
        # trec prin fiecare cos asociat consumatorului
        for cart in self.carts:
            # creez un cos nou
            cart_id = self.marketplace.new_cart()
            for action in cart:
                pr_type, quantity, product = action["type"], action["quantity"], action["product"]
                if pr_type == "add": # daca trebuie sa adaug produse
                    for _ in range(0, quantity):
                        # adaug produsul in cos
                        added = self.marketplace.add_to_cart(cart_id, product)
                        if not added:
                            # daca nu am reusit, astept retry_time secunde si incerc din nou
                            while not added:
                                sleep(self.retry_time)
                                added = self.marketplace.add_to_cart(cart_id, product)
                else: # daca trebuie sa scot produse
                    for _ in range(quantity):
                        # scot produsul din cos
                        self.marketplace.remove_from_cart(cart_id, product)

            # plasez comanda
            final_products = self.marketplace.place_order(cart_id)

            # afisez produsele cumparate
            for bought_product in final_products:
                print(f"{self.name} bought {bought_product}", flush=True)
