from locust import HttpLocust, TaskSet, task

class UserBehavior(TaskSet):
  def on_start(self):
    """ on_start is called when a Locust start before any task is scheduled """
    #self.login()
    pass

  def login(self):
    self.client.post("/login", {"username":"a_user", "password":"a_password"})

  @task(1)
  def index(self):
    self.client.get("/register")

  '''
  @task(2)
  def profile(self):
    self.client.get("/profile")
  '''

class WebsiteUser(HttpLocust):
  task_set = UserBehavior
  min_wait = 1000
  max_wait = 3000