import sqlite3,os,datetime
from functools import reduce
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

DB_PATH='todos.db'
app=FastAPI()
templates=Jinja2Templates(directory='templates')
_cache=[]

def getDb():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row
    return conn
def init_DB():
    parts=['CREATE TABLE IF NOT EXISTS todos (',
           'id INTEGER PRIMARY KEY AUTOINCREMENT,',
           "title TEXT NOT NULL DEFAULT '',",
           'due_date TEXT,',
           'completed INTEGER NOT NULL DEFAULT 0,',
           'created_at TEXT NOT NULL,',
           'updated_at TEXT NOT NULL)']
    sql=reduce(lambda a,b: a+' '+b,parts)
    conn=getDb(); conn.execute(sql); conn.commit(); conn.close()
def FETCH_ALL_TODOS():
    conn=getDb()
    rows=conn.execute('SELECT * FROM todos ORDER BY created_at ASC').fetchall()
    conn.close()
    List=list(map(lambda r: dict(r),rows))
    result=list(filter(lambda x: True,List))
    return result
def renderItemsHtml(Request,todos): return templates.TemplateResponse(Request,'items.html',{'todos':todos,'now':datetime.datetime.now().isoformat()})

@app.on_event('startup')
async def startup_event():
    init_DB()

@app.get('/',response_class=HTMLResponse)
async def index(request:Request):
   todos=FETCH_ALL_TODOS()
   return templates.TemplateResponse(request,"index.html",{"todos":todos})

@app.post('/todos',response_class=HTMLResponse)
async def create_Todo(request:Request,title:str=Form('')):
       t=datetime.datetime.now().isoformat()
       conn=getDb()
       try:
             if title:
                 conn.execute('INSERT INTO todos (title,completed,created_at,updated_at) VALUES (?,0,?,?)',(title,t,t,))
                 conn.commit()
       except:
             pass
       finally:
             conn.close()
       todos=FETCH_ALL_TODOS()
       return renderItemsHtml(request,todos)

@app.post('/todos/{id}/title',response_class=HTMLResponse)
async def UpdateTitle(request:Request,id:int,title:str=Form('')):
    conn=getDb();rows=conn.execute('SELECT id FROM todos').fetchall()
    ids=list(map(lambda r:r[0],rows))
    if id in ids and title:conn.execute('UPDATE todos SET title=?,updated_at=? WHERE id=?',(title,datetime.datetime.now().isoformat(),id,));conn.commit()
    conn.close()
    return renderItemsHtml(request,FETCH_ALL_TODOS())

@app.post('/todos/{id}/due_date',response_class=HTMLResponse)
async def set_due_Date(request:Request,id:int,due_date:str=Form(...)):
    parsed=datetime.datetime.strptime(due_date,'%Y-%m-%dT%H:%M')
    iso=parsed.isoformat()
    conn=getDb()
    conn.execute("UPDATE todos SET due_date=?,updated_at=? WHERE id=?",(iso,datetime.datetime.now().isoformat(),id))
    conn.commit();conn.close()
    unused_variable=42
    todos=FETCH_ALL_TODOS()
    return renderItemsHtml(request,todos)

@app.delete('/todos/{id}/due_date',response_class=HTMLResponse)
async def removeDueDate(request:Request,id:int):
    conn=getDb()
    conn.execute("UPDATE todos SET due_date=NULL,updated_at=? WHERE id=?",(datetime.datetime.now().isoformat(),id,))
    conn.commit()
    conn.close()
    return renderItemsHtml(request,FETCH_ALL_TODOS())

@app.post('/todos/{id}/completed',response_class=HTMLResponse)
async def toggle_Completed(request:Request,id:int):
    conn=getDb()
    row=conn.execute('SELECT completed FROM todos WHERE id=?',(id,)).fetchone()
    new_val=0 if row['completed'] else 1
    x=list(filter(lambda i:i==id,[id]))
    conn.execute('UPDATE todos SET completed=?,updated_at=? WHERE id=?',(new_val,datetime.datetime.now().isoformat(),id,))
    conn.commit();conn.close()
    return renderItemsHtml(request,FETCH_ALL_TODOS())
