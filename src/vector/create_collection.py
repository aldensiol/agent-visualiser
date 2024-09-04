from pymilvus import (
    utility,
    CollectionSchema, DataType, FieldSchema, Collection
)

COLLECTION_NAME = "vector_index"

def drop_collection(collection_name):
    # Check if the collection exists
    if utility.has_collection(collection_name):
        collection = Collection(name=collection_name)
        # Release the collection
        collection.release()
        # Drop the collection if it exists
        utility.drop_collection(collection_name)
        print(f"Collection '{collection_name}' has been dropped")
    else:
        print(f"Collection '{collection_name}' does not exist")

AUTO_ID = FieldSchema(
    name="pk",
    dtype=DataType.INT64,
    is_primary=True,
    auto_id=True)

DOC_ID = FieldSchema(
    name="doc_id",
    dtype=DataType.VARCHAR,
    max_length=500
)

DOC_SOURCE = FieldSchema(
    name="doc_source",
    dtype=DataType.VARCHAR,
    max_length=1000,
    default_value="NA"
)

DOC_CONTENT = FieldSchema(
    name="text",
    dtype=DataType.VARCHAR,
    max_length=50000,
    default_value=""
)

DENSE_EMBEDDINGS = FieldSchema(
    name="dense_embeddings",
    dtype=DataType.FLOAT_VECTOR,
    dim=1024
)

SPARSE_EMBEDDINGS = FieldSchema(
    name="sparse_embeddings",
    dtype=DataType.SPARSE_FLOAT_VECTOR
)

SCHEMA = CollectionSchema(
  fields=[AUTO_ID, DOC_ID, DOC_SOURCE, DOC_CONTENT, DENSE_EMBEDDINGS, SPARSE_EMBEDDINGS],
  description="milvus_schema",
  enable_dynamic_field=True
)

def create_collection(collection_name, schema):
    # Check if the collection exists
    if utility.has_collection(collection_name):
        print(f"Collection '{collection_name}' already exists")
    # Create the collection
    return Collection(name=collection_name, schema=schema, using='default', shards_num=2)