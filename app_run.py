import uvicorn

from bootstrap import bootstrap
app = bootstrap()

if __name__ == "__main__":
    uvicorn.run("app_run:app", host="0.0.0.0", port=9000, debug=True, log_config="uvicorn_config.json")

