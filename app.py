from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from dotenv import load_dotenv

# 加载环境变量（本地开发用）
load_dotenv()

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取 Neon.tech 数据库连接
def get_db_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

# 创建数据表（首次运行执行）
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 保存数据接口
@app.post("/items")
async def create_item(content: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (content) VALUES (%s) RETURNING id",
        (content,)
    )
    item_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return {"id": item_id, "content": content}

# 查询数据接口
@app.get("/items")
async def read_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, created_at FROM items")
    items = cur.fetchall()
    conn.close()
    return [
        {"id": row[0], "content": row[1], "created_at": row[2]}
        for row in items
    ]
