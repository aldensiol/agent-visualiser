from pymilvus import AnnSearchRequest, RRFRanker
from services.services import collection, bge_embed_model, splade_embed_model

def hybrid_search(query: str) -> str:
    dense_embedding = list(bge_embed_model.query_embed(query))[0]
    sparse_embedding = list(splade_embed_model.encode_queries([query]))
    
    search_results = collection.hybrid_search(
            reqs=[
                AnnSearchRequest(
                    data=[dense_embedding],  # content vector embedding
                    anns_field='dense_embeddings',  # content vector field
                    param={"metric_type": "COSINE", "params": {"M": 64, "efConstruction": 512}}, # Search parameters
                    limit=3
                ),
                AnnSearchRequest(
                    data=list(sparse_embedding),  # keyword vector embedding
                    anns_field='sparse_embeddings',  # keyword vector field
                    param={"metric_type": "IP", "params": {"drop_ratio_build": 0.2}}, # Search parameters
                    limit=3
                )
            ],
            output_fields=['doc_id', 'text', 'doc_source'],
            # Use WeightedRanker to combine results with specified weights
            # Alternatively, use RRFRanker for reciprocal rank fusion reranking
            rerank=RRFRanker(),
            limit=3
            )
    
    hits = search_results[0]
    
    context = []
    for res in hits:
        text = res.text
        source = res.doc_source
        context.append(f"Source: {source}\nContext: {text}")
    
    return "\n\n".join(context)