import uuid
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, select, update, delete
from dataclasses import dataclass

engine = create_engine("sqlite:///data.db", echo=True)
metadata = MetaData()

entries_table = Table("entries", metadata,
                      Column("id", String, primary_key=True, nullable=False),
                      Column("name", String, nullable=False),
                      Column("amount", Float, nullable=False),
                      Column("category", String))

def init_db():
    metadata.create_all(engine)
    print("Database initialized and tables created.")

@dataclass
class Entry:
    id: uuid.UUID
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: str, name: str, amount: float, category: str | None):
        return cls(
            uuid.UUID(id),
            name,
            amount,
            category,
        )

def create_entry(name: str, amount: float, category: str | None = None) -> None:
    entry_id = uuid.uuid4().hex
    stmt = entries_table.insert().values(id=entry_id, name=name, amount=amount, category=category)

    with engine.begin() as conn:
        conn.execute(stmt)

def get_entry(id: uuid.UUID) -> Entry:
    stmt = select(entries_table).where(entries_table.c.id == id.hex)

    with engine.begin() as conn:
        result = conn.execute(stmt).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entry not found")

def get_all_entries() -> list[Entry]:
    stmt = select(entries_table)

    with engine.begin() as conn:
        results = conn.execute(stmt).fetchall()
        return [Entry.from_db(*r) for r in results]

def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
    stmt = update(entries_table).where(entries_table.c.id == id.hex).values(name=name, amount=amount, category=category)
    with engine.begin() as conn:
        conn.execute(stmt)

def delete_entry(id: uuid.UUID) -> None:
    stmt = delete(entries_table).where(entries_table.c.id == id.hex)

    with engine.begin() as conn:
        conn.execute(stmt)


