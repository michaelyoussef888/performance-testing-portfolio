import random
from locust import HttpUser, task, between, LoadTestShape
class Shopper(HttpUser):
    wait_time = between(0.5, 2)
    def on_start(self):
        self.client.post("/api/login", name="01 Login")
    @task(5)
    def browse(self): self.client.get(f"/api/products?page={random.randint(1,50)}", name="02 Browse catalogue")
    @task(4)
    def view(self): self.client.get(f"/api/products/{random.randint(1,2000)}", name="03 Product details")
    @task(2)
    def search(self): self.client.get(f"/api/search?q={random.randint(1,99)}", name="04 Search")
    @task(2)
    def add(self): self.client.post("/api/cart", json={"product_id": random.randint(1,2000), "qty": 1}, name="05 Add to cart")
    @task(1)
    def checkout(self): self.client.post("/api/checkout", name="06 Checkout")
class Steps(LoadTestShape):
    # step load: 50 -> 100 -> 200 -> 300 users, 60 s each, ramp 5 users/s
    steps = [(60, 50), (120, 100), (180, 200), (240, 300)]
    def tick(self):
        t = self.get_run_time()
        for end, users in self.steps:
            if t < end: return (users, 5)
        return None
