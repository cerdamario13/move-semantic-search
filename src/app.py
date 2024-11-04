from quart import Quart, request, jsonify
import models

app = Quart(__name__)

@app.route('/status')
async def status():
    return jsonify({'status': 'ok'})

@app.route('/search', methods=['POST'])  # Change to POST for JSON body
async def search():
    data = await request.get_json()  # Retrieve JSON body
    query = data.get('query', '')  # Get query field from JSON

    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        embedding = await models.get_embeddings(query)  # Await the async call
        similar_documents = await models.find_similar_documents(embedding)
        serialized_documents = [models.serialize_document(doc) for doc in similar_documents]

        result = [document['title'] for document in serialized_documents]
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': 'Error in query search'}), 500
    
    finally:
        models.client.close()

if __name__ == "__main__":
    app.run(port=5000)
