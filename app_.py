from flask import Flask, render_template, request, url_for
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from crawler_ import website_crawler_and_indexer

app = Flask(__name__)

# Path to the Whoosh index directory
INDEX_DIR = "indexdir"
SEED_URL = "https://vm009.rz.uos.de/crawl/index.html"  # Replace with your seed URL

# Step 1: Run the crawler and populate the Whoosh index
website_crawler_and_indexer(SEED_URL)

# Flask Routes
@app.route('/')
def home():
    """
    Render the homepage with the search form.
    """
    return render_template('home.html')

@app.route('/search', methods=['GET'])
def search():
    """
    Handle the search query and return results from the Whoosh index.
    """
    query = request.args.get('query', '')
    results = []

    if query:
        # Step 2: Open the Whoosh index and search for the query
        ix = open_dir(INDEX_DIR)
        with ix.searcher() as searcher:
            parser = QueryParser("content", ix.schema)
            parsed_query = parser.parse(query)
            whoosh_results = searcher.search(parsed_query)
            for result in whoosh_results:
                results.append({
                    "url": result["url"],
                    "title": result["title"],
                    "teaser": result.highlights("content")  # Highlight matching terms
                })

    return render_template('results.html', query=query, results=results)

@app.route('/about')
def about():
    """
    Render the about page.
    """
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
