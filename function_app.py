import azure.functions as func
import json
import logging
from qa import answer_question
from site_crawler import crawl_site

app = func.FunctionApp()


@app.function_name(name="indexer")
@app.route(route="index", methods=["POST"])
def indexer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    site_url = req_body.get("url")
    force_update = bool(req_body.get("force_update", False))

    if not site_url:
        response = {
            "error": "BAD_REQUEST_INVALID_URL"
        }
        return func.HttpResponse(json.dumps(response), status_code=400, mimetype="application/json")
    else:
        crawl_site(site_url, force_update)
        response = {
            "url": site_url,
            "force_update": force_update,
            "message": f"Crawled {site_url} successfully"
        }
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )


@app.function_name(name="bot")
@app.route(route="v1/answer", methods=["POST"])
def bot(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    question = req_body.get("question")
    
    logging.info(f"Question: {question}")
    answer = answer_question(question)
    response = {
        "question": question,
        "answer": answer
    }

    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype="application/json"
    )
