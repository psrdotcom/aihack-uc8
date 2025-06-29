from Utils import get_postgresql_connection

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from collections import defaultdict
import pickle
import json

class NewsArticleIndexer:
    """
    Multi-algorithm news article indexer with various similarity detection methods
    """
    
    def __init__(self, embedding_model='all-MiniLM-L6-v2', use_gpu=False):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        if use_gpu:
            self.embedding_model = self.embedding_model.cuda()
            
        # Initialize various indexing structures
        self.articles = []
        self.embeddings = None
        self.faiss_index = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.graph = None
        
    def add_articles(self, articles):
        """Add articles to the indexer"""
        self.articles.extend(articles)
        self._build_indices()
    
    def preprocess_text(self, article):
        """Enhanced preprocessing for better relevance"""
        # Combine title (weighted more heavily) and content
        title_weight = 2  # Give title more importance
        return f"{' '.join([article['title']] * title_weight)} {article.get('location_mention', '')} {article.get('officals_involved', '')} {article.get('relevance_category', '')}"

    def _build_indices(self):
        """Build all indexing structures"""
        texts = [self.preprocess_text(article) for article in self.articles]
        
        # 1. SEMANTIC EMBEDDINGS (Best for semantic similarity)
        print("Building semantic embeddings...")
        self.embeddings = self.embedding_model.encode(texts, convert_to_tensor=True)
        
        # 2. FAISS INDEX (Best for large-scale retrieval)
        print("Building FAISS index...")
        self._build_faiss_index()
        
        # 3. TF-IDF (Best for keyword-based similarity)
        print("Building TF-IDF index...")
        self._build_tfidf_index(texts)
        
        # 4. GRAPH-BASED (Best for discovering article networks)
        print("Building article graph...")
        self._build_article_graph()
    
    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        d = self.embeddings.shape[1]
        
        # For small datasets: IndexFlatL2 (exact search)
        # For large datasets: IndexIVFFlat (approximate search)
        if len(self.articles) < 10000:
            self.faiss_index = faiss.IndexFlatL2(d)
        else:
            # Use IVF for larger datasets
            nlist = min(100, len(self.articles) // 10)  # number of clusters
            quantizer = faiss.IndexFlatL2(d)
            self.faiss_index = faiss.IndexIVFFlat(quantizer, d, nlist)
            # Train the index
            self.faiss_index.train(self.embeddings.cpu().numpy())
        
        self.faiss_index.add(self.embeddings.cpu().numpy())
    
    def _build_tfidf_index(self, texts):
        """Build TF-IDF index for keyword-based similarity"""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            min_df=1,
            max_df=0.95
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
    
    def _build_article_graph(self, similarity_threshold=0.3):
        """Build graph of related articles"""
        self.graph = nx.Graph()
        
        # Add all articles as nodes
        for i, article in enumerate(self.articles):
            self.graph.add_node(i, **article)
        
        # Add edges based on similarity
        for i in range(len(self.articles)):
            similar_articles = self.find_similar_semantic(i, k=5, return_scores=True)
            for j, score in similar_articles:
                if i != j and score > similarity_threshold:
                    self.graph.add_edge(i, j, weight=score)
    
    # ===== SIMILARITY SEARCH METHODS =====
    
    def find_similar_semantic(self, query_idx, k=5, return_scores=False):
        """Find similar articles using semantic embeddings (BEST for meaning)"""
        query_embedding = self.embeddings[query_idx].cpu().numpy().reshape(1, -1)
        
        # Search using FAISS
        distances, indices = self.faiss_index.search(query_embedding, k + 1)
        
        # Remove the query article itself
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != query_idx:
                similarity_score = 1 / (1 + dist)  # Convert distance to similarity
                if return_scores:
                    results.append((idx, similarity_score))
                else:
                    results.append(idx)
                if len(results) >= k:
                    break
        
        return results
    
    def find_similar_tfidf(self, query_idx, k=5, return_scores=False):
        """Find similar articles using TF-IDF (BEST for keywords)"""
        query_vector = self.tfidf_matrix[query_idx]
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top-k similar articles (excluding self)
        similar_indices = similarities.argsort()[::-1]
        results = []
        
        for idx in similar_indices:
            if idx != query_idx and len(results) < k:
                if return_scores:
                    results.append((idx, similarities[idx]))
                else:
                    results.append(idx)
        
        return results
    
    def find_similar_hybrid(self, query_idx, k=5, semantic_weight=0.7, return_scores=False):
        """Hybrid approach combining semantic and TF-IDF (BEST overall)"""
        # Get semantic similarities
        semantic_results = self.find_similar_semantic(query_idx, k=k*2, return_scores=True)
        tfidf_results = self.find_similar_tfidf(query_idx, k=k*2, return_scores=True)
        
        # Combine scores
        combined_scores = defaultdict(float)
        
        for idx, score in semantic_results:
            combined_scores[idx] += semantic_weight * score
            
        for idx, score in tfidf_results:
            combined_scores[idx] += (1 - semantic_weight) * score
        
        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        if return_scores:
            return sorted_results[:k]
        else:
            return [idx for idx, _ in sorted_results[:k]]
    
    def find_similar_graph(self, query_idx, k=5):
        """Find similar articles using graph-based methods"""
        if not self.graph.has_node(query_idx):
            return []
        
        # Get neighbors sorted by edge weight
        neighbors = list(self.graph.neighbors(query_idx))
        neighbor_weights = [(n, self.graph[query_idx][n]['weight']) for n in neighbors]
        neighbor_weights.sort(key=lambda x: x[1], reverse=True)
        
        return [idx for idx, _ in neighbor_weights[:k]]
    
    # ===== ADVANCED ANALYSIS METHODS =====
    
    def detect_article_clusters(self, method='semantic', n_clusters=None):
        """Detect clusters of related articles"""
        from sklearn.cluster import KMeans, DBSCAN
        
        if method == 'semantic':
            features = self.embeddings.cpu().numpy()
        elif method == 'tfidf':
            features = self.tfidf_matrix.toarray()
        
        if n_clusters:
            clusterer = KMeans(n_clusters=n_clusters, random_state=42)
        else:
            clusterer = DBSCAN(eps=0.5, min_samples=2)
        
        cluster_labels = clusterer.fit_predict(features)
        
        # Group articles by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            clusters[label].append(i)
        
        return dict(clusters)
    
    def find_trending_topics(self, time_window_hours=24):
        """Find trending topics (if articles have timestamps)"""
        # This would require timestamp information in articles
        # Implementation would filter recent articles and cluster them
        pass
    
    def get_article_importance_scores(self):
        """Calculate importance scores using PageRank on article graph"""
        if self.graph is None:
            return {}
        
        pagerank_scores = nx.pagerank(self.graph, weight='weight')
        return pagerank_scores
    
    def save_index(self, filepath):
        """Save the entire index to disk"""
        index_data = {
            'articles': self.articles,
            'embeddings': self.embeddings.cpu().numpy() if self.embeddings is not None else None,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'graph': self.graph
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        
        # Save FAISS index separately
        if self.faiss_index is not None:
            faiss.write_index(self.faiss_index, f"{filepath}.faiss")
    
    def load_index(self, filepath):
        """Load index from disk"""
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.articles = index_data['articles']
        self.embeddings = index_data['embeddings']
        self.tfidf_vectorizer = index_data['tfidf_vectorizer']
        self.tfidf_matrix = index_data['tfidf_matrix']
        self.graph = index_data['graph']
        
        # Load FAISS index
        try:
            self.faiss_index = faiss.read_index(f"{filepath}.faiss")
        except:
            print("Could not load FAISS index, rebuilding...")
            self._build_faiss_index()

# ===== USAGE EXAMPLE =====

def main():
    # Sample articles
    conn = get_postgresql_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM articles order by article_id asc"
    cursor.execute(query)
    articles_db = cursor.fetchall()
    articles = [{} for _ in range(len(articles_db))]
    for i, article in enumerate(articles_db):
        articles[i] = {
            "article_id": article[0],
            "title": article[1],
            # "content": article[2],
            "location_mention": article[5],
            "officals_involved": article[6],
            "relevance_category": article[7],
        }
    
    # Initialize indexer
    indexer = NewsArticleIndexer()
    indexer.add_articles(articles)
    
    # Test different similarity methods
     # "President Signs New Trade Deal"
    for i, article in enumerate(articles):
        query_idx = i
        print(f"\n🔍 i: '{i}'")
        print(f"\n🔍 Finding articles similar to: '{articles[query_idx]['title']}'")
        linked_id = []
        print("\n1.  Semantic Similarity (Best for meaning):")
        semantic_results = indexer.find_similar_semantic(query_idx, k=3)
        for idx in semantic_results:
            linked_id.append(articles[idx]['article_id'])
            print(f"   - {articles[idx]['title']}")
        
        # print("\n2.  TF-IDF Similarity (Best for keywords):")
        # tfidf_results = indexer.find_similar_tfidf(query_idx, k=3)
        # for idx in tfidf_results:
        #     print(f"   - {articles[idx]['title']}")
        
        print("\n3. Hybrid Similarity (Best overall):")
        hybrid_results = indexer.find_similar_hybrid(query_idx, k=3)
        for idx in hybrid_results:
            print(f"   - {articles[idx]['title']}")
        cursor.execute("UPDATE articles SET linked_id = %s WHERE article_id = %s", (linked_id, articles[query_idx]['article_id']))
        conn.commit()
        # print("\n4. Graph-based Similarity:")
        # graph_results = indexer.find_similar_graph(query_idx, k=3)
        # for idx in graph_results:
        #     print(f"   - {articles[idx]['title']}")
        
        # # Detect clusters
        # print("\n Article Clusters:")
        # clusters = indexer.detect_article_clusters(method='semantic')
        # for cluster_id, article_indices in clusters.items():
        #     if cluster_id != -1:  # Ignore noise cluster
        #         print(f"Cluster {cluster_id}:")
        #         for idx in article_indices:
        #             print(f"   - {articles[idx]['title']}")
        
        # Calculate importance scores
        # print("\n Article Importance Scores:")
        # importance_scores = indexer.get_article_importance_scores()
        # sorted_importance = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        # for idx, score in sorted_importance[:3]:
        #     print(f"   {score:.3f} - {articles[idx]['title']}")

if __name__ == "__main__":
    main()