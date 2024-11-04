import openai
import config
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB]
collection = db[config.MONGO_COLLECTION]
openai.api_key = config.OPENAI_API_KEY

async def get_embeddings(query):
    try:
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        return response.data[0].embedding
    except Exception as e:
        raise ValueError(f"Failed to get embeddings")
    

async def find_similar_documents(embedding):
    try:
        # pipeline where the output of one step is the input to the next.
        pipeline = [
            {
                # vectorSearch is a MongoDB aggregation operator used to perform similarity searches based on vector embeddings.
                "$vectorSearch": {
                    # embedding is compared against vectors in plot_embedding field.
                    "queryVector": embedding,
                    "path": "plot_embedding",
                    # numCandidates specifies how many candidate vectors are retrieved from the database before any further processing is applied. A larger value can increase the likelihood of retrieving more relevant results but may require more computational resources and time for processing.
                    "numCandidates": 100,
                    "limit": 3,
                    "index": "vector_index",
                }
            }
        ]

        # The aggregate() method is used to perform data processing through aggregation pipelines. It allows to analyze and manipulate data stored in collections by applying a series of operations to the documents.
        documents = list(collection.aggregate(pipeline))
        return documents

    except Exception as e:
        raise LookupError(f"Failed to find similar documents") from e
    

def serialize_document(doc):
    """Convert a MongoDB document to a serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc
