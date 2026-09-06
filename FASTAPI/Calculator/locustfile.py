from locust import HttpUser, task, between


class CalculatorUser(HttpUser):

    wait_time = between(0.01, 0.05)

    @task
    def calculate(self):
        self.client.post(
            "/calculate",
            json={
                "num1": 20,
                "symbol": "+",
                "num2": 30
            }
        )