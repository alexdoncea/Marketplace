"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, daemon=kwargs["daemon"])
        self.name = kwargs["name"]
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time

    def run(self):
        # inregistrez producatorul si creez un id unic
        producer_id = self.marketplace.register_producer()
        while True:
            # pentru fiecare produs din lista de produse
            for (product, quantity, produce_time) in self.products:
                # produc produsele in cantitatea specificata
                for _ in range(quantity):
                    sleep(produce_time)
                    # public produsul in marketplace
                    published = self.marketplace.publish(producer_id, product)
                    while not published: # daca nu am reusit, astept si incerc din nou
                        sleep(self.republish_wait_time)
                        published = self.marketplace.publish(producer_id, product)
