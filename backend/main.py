import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from starlette.responses import FileResponse

from connect_api import authentication, create_print_job, upload_print_file, execute_print
from connect_request import ConnectRequest
from generate_request import GenerateRequest
from generate import generate_file
from register_information_request import RegisterInformationRequest

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/connect")
async def connect(connect_request: ConnectRequest):
    return authentication(connect_request.device, connect_request.password)

@app.post("/register-information")
async def register_information(register_information: RegisterInformationRequest):
    json_file = 'information.json'
    with open(json_file, 'w') as f:
        json.dump(register_information.dict(), f, ensure_ascii=False)
    print(f'JSON 파일 {json_file}에 저장되었습니다.')

@app.post("/generate")
async def generate(generate_request: GenerateRequest):
    generate_file(generate_request)
    return FileResponse(path="file_to_show.html", media_type='text/html')


@app.post("/print")
async def print_execute(
    file: UploadFile = File(...),
    subject_id: str = Form(...),
    access_token: str = Form(...),
):

    file_path = "file_to_print.html"

    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    job_info = create_print_job(subject_id, access_token)
    upload_print_file(job_info["id"], job_info["upload_uri"])
    execute_print(subject_id, access_token, job_info["id"])