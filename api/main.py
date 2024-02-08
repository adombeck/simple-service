# Copyright 2024 Flower Labs GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import crypt
import sys
from typing import Optional

import bcrypt
from fastapi import FastAPI, HTTPException, status
from sqlmodel import create_engine, SQLModel, Field, Session, select


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str = Field()


app = FastAPI()

DATABASE_URL = "postgresql://postgres:postgres@postgres/db"

print(f"DATABASE_URL: {DATABASE_URL}", file=sys.stderr)
engine = create_engine(DATABASE_URL)


@app.on_event("startup")
def on_startup():
    # Create DB and tables
    SQLModel.metadata.create_all(engine)


@app.post("/signup")
def signup(user: User):
    # TODO: Check that user's can't set their own IDs
    # TODO: Validate email
    # TODO: Password checks

    user.password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.post("/signin")
def signin(user: User):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.email == user.email)).first()
        if not db_user:
            print("No user found for email", file=sys.stderr)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if bcrypt.hashpw(user.password.encode(), db_user.password.encode()) != db_user.password.encode():
            print("Incorrect password", file=sys.stderr)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return db_user


@app.get("/")
def read_root():
    return {"Hello": "World"}
