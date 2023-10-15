from locust import HttpUser, task, constant


class WebsiteUser(HttpUser):
    host = "https://tanzquotient.org"

    # wait_time = constant(1)

    # ----- Main pages -----

    @task
    def index(self):
        self.client.get("/")

    @task(weight=4)
    def courses(self):
        self.client.get("/en/courses/")

    @task(weight=4)
    def events(self):
        self.client.get("/en/events/")

    @task
    def partner(self):
        self.client.get("/en/partner/")

    @task
    def services(self):
        self.client.get("/en/services/")

    @task
    def photos(self):
        self.client.get("/en/photos/")

    @task
    def about(self):
        self.client.get("/en/about/")

    @task
    def faq(self):
        self.client.get("/en/faq/")

    # ----- Detail pages -----

    @task(weight=3)
    def course_details(self):
        for id in range(100_650, 100_700):
            self.client.get(
                "/en/courses/%s/detail/" % id, name="/en/courses/[id]/detail/"
            )
