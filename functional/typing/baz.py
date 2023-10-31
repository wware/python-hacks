# https://docs.pydantic.dev/usage/validators/

from pydantic import BaseModel, validator, root_validator
from contextlib import contextmanager


@contextmanager
def expect_failure():
    successful = False
    try:
        yield
        successful = True
    except Exception:
        print("OK: validation error was expected")
    finally:
        if successful:
            raise Exception("That should have failed")


class UserModel(BaseModel, frozen=True):
    name: str
    username: str
    password1: str
    password2: str

    @validator('name')
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()

    @validator('password2')
    def passwords_match(cls, v, values):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v


class Customer(BaseModel, frozen=True):
    name: str
    phone: str

    @root_validator()
    @classmethod
    def validate_all_fields_at_the_same_time(cls, field_values):
        import re
        name = field_values['name']
        phone = field_values['phone']
        assert name != "invalid_name", name
        assert re.match(r"\d{3}-\d{4}", phone)
        return field_values


class ComplexNumber(BaseModel, frozen=True):
    x: float
    y: float

    @root_validator()
    @classmethod
    def check_size(cls, values):
        x = values['x']
        y = values['y']
        if x**2 + y**2 > 5**2:
            raise ValueError('too big')
        return values


####################################################

print(UserModel(
    name='samuel colvin',
    username='scolvin',
    password1='zxcvbn',
    password2='zxcvbn',
))


with expect_failure():
    UserModel(
        name='samuel',
        username='scolvin',
        password1='zxcvbn',
        password2='zxcvbn',
    )

with expect_failure():
    UserModel(
        name='samuel',
        username='scolvin',
        password1='zxcvbn',
        password2='zxcvbn2',
    )


print(ComplexNumber(x=3, y=-4))
with expect_failure():
    print(ComplexNumber(x=179, y=0))
print(ComplexNumber(x="1", y="2"))


print(Customer(name="Fred", phone="867-5309"))
with expect_failure():
    print(Customer(name="invalid_name", phone="867-5309"))
with expect_failure():
    print(Customer(name="Fred", phone="86-5309"))
with expect_failure():
    print(Customer(name="Fred", phone="867-53@9"))
