from src.api import schemas as p

user1 = p.CreateUserSchema(
    email="u1@mail.com",
    first_name="u1",
    last_name="",
    password="secret"
)
user2 = p.CreateUserSchema(
    email="u2@mail.com",
    first_name="u2",
    last_name="",
    password="secret"
)
baseUrl = "http://127.0.0.1:8000/"
