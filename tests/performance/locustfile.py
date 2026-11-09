from locust import HttpUser, between, task


class Customer(HttpUser):
    wait_time = between(1, 2)      # har user 1-2 second ruk ke agla kaam karta hai

    @task(5)                        # weight 5: zyada baar chalega
    def browse_restaurants(self):
        self.client.get("/restaurants?page=1&page_size=10")

    @task(2)
    def filter_restaurants(self):
        self.client.get("/restaurants?cuisine=italian&min_rating=4")

    @task(1)
    def search_by_name(self):
        self.client.get("/restaurants?q=biryani")