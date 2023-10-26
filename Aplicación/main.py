from typing import Optional
from fastapi import FastAPI, Body, Request, Form,UploadFile,File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pandas as pd
from joblib import dump, load
import os
from fastapi import FastAPI, HTTPException
from unidecode import unidecode
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
import io


app = FastAPI()

filename = 'results.csv'

template = Jinja2Templates(directory="html")
app.mount("/static", StaticFiles(directory="html/static"), name = "static")
    
@app.get("/",response_class=HTMLResponse)
def read_root(request: Request):
   return template.TemplateResponse("index.html",{"request":request})

@app.post("/submit")
def handle_form(request:Request, cajita: str = Form(...)):
   pipeline_loaded = load("html/static/assets/model.joblib")
   data = {'Textos_espanol': [cajita], 'sdg': 0}
   df = pd.DataFrame(data)
   df["sdg"][0] = pipeline_loaded.predict(df['Textos_espanol'])
   print(['sdg'][0])
   msg = ""
   if df["sdg"][0] == 3:
      msg = "3"
   elif df["sdg"][0] == 4:
      msg= "4"
   else:
      msg="5"
   print(msg)
   
   return template.TemplateResponse("index.html",{"request":request,"msg":msg})

@app.post("/file_analisis")
async def predict_from_file(request: Request, file: UploadFile):
   print("Entro file")
   # Check if uploaded file is CSV
   ext = os.path.splitext(file.filename)[1]
   if ext.lower() not in ['.csv']:
      return "Error: Only CSV files allowed"

   # Read the CSV file into a Pandas DataFrame
   contents = await file.read()
   df = pd.read_csv(io.BytesIO(contents), encoding="utf-8", sep=';')
   pipeline_loaded = load("html/static/assets/model.joblib")
   df["sdg"] = pipeline_loaded.predict(df["Textos_espanol"])
   df.to_csv(filename, index=False)
   
   return template.TemplateResponse("index.html",{"request":request})

@app.get("/file_analisis")
def read_item(request: Request):
   return template.TemplateResponse("index.html",{"request":request})

@app.get("/download")
async def get_data():
    return FileResponse(filename, filename="/results.csv")