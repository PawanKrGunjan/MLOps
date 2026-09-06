from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Union, Literal
import uvicorn


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Demo users only. Use a database and password hashing in a real application.
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "pawan": {"password": "user123", "role": "user"},
}
active_tokens = {}
TOKEN_EXPIRE_MINUTES = 30


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = USERS.get(username)

    if user is None or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = token_urlsafe(32)
    active_tokens[token] = {
        "username": username,
        "role": user["role"],
        "expires_at": datetime.now(timezone.utc)
        + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }

    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = active_tokens.get(token)

    if user is None or user["expires_at"] <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(user: Annotated[dict, Depends(get_current_user)]):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user


@app.get("/")
async def index(user: Annotated[dict, Depends(get_current_user)]):
    #return {"message": "Hello World"}
    return f"Mathematics Claculator"

# Calculator input schema
class CalculatorInput(BaseModel):
    num1: Union[int, float]
    symbol: Literal['+', '-', '*', '/']
    num2: Union[int, float]

# Calculator logic
class Calculator:
    def __init__(self, num1: Union[int, float], symbol: str, num2: Union[int, float]):
        self.num1 = num1
        self.symbol = symbol
        self.num2 = num2

    def calculate(self) -> float:
        if self.symbol == '+':
            return self.num1 + self.num2
        elif self.symbol == '-':
            return self.num1 - self.num2
        elif self.symbol == '*':
            return self.num1 * self.num2
        elif self.symbol == '/':
            if self.num2 == 0:
                raise ValueError("Division by zero is not allowed")
            return self.num1 / self.num2
        else:
            raise ValueError("Invalid operation")

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    user: Annotated[dict, Depends(require_admin)],
):
    return {
        "message": f"User {user_id} deleted"
    }

@app.post("/calculate")
async def calculate(
    data: CalculatorInput,
    user: Annotated[dict, Depends(get_current_user)],
):
    try:
        calc = Calculator(data.num1, data.symbol, data.num2)
        result = calc.calculate()
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# form-data endpoint
@app.post("/calculate-form")
async def calculate_form(
    user: Annotated[dict, Depends(get_current_user)],
    num1: float = Form(...),
    symbol: str = Form(...),
    num2: float = Form(...),
):
    try:
        calc = Calculator(num1, symbol, num2)
        result = calc.calculate()
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
   uvicorn.run("Ganesh:app", host="127.0.0.1", port=8000, reload=True)
