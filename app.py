from flask import Flask, render_template, request

from search import search

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    result = {"title": "", "content": "", "source_url": "", "source_label": "", "confidence": 0}
    error_message = ""

    if request.method == "POST":
        query = request.form.get("question", "").strip()
        if query:
            try:
                result = search(query)
            except Exception as error:
                error_message = str(error)

    return render_template("index.html", query=query, result=result, error_message=error_message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
