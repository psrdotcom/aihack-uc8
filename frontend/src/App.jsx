import { useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE?.replace(/\/$/, '') || '';

function App() {
  const [task, setTask] = useState('echo')
  const [params, setParams] = useState('{}')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState("")
  const [searchResults, setSearchResults] = useState([])
  const [lambdaTestResult, setLambdaTestResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    let paramsObj = {}
    try {
      paramsObj = params ? JSON.parse(params) : {}
    } catch (err) {
      setError('Params must be valid JSON')
      return
    }
    try {
      const res = await fetch(`${API_BASE}/agent/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, params: paramsObj })
      })
      if (!res.ok) throw new Error('Request failed')
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault();
    setError(null);
    setSearchResults([]);
    try {
      const res = await fetch(`${API_BASE}/agent/relevance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: 'relevance', params: { criteria: search.split(',').map(s => s.trim()).filter(Boolean) } })
      });
      if (!res.ok) throw new Error('Search failed');
      const data = await res.json();
      setSearchResults(data.details.relevant_articles || []);
    } catch (err) {
      setError(err.message);
    }
  };

  const testLambdaUrl = async () => {
    setError(null);
    setLambdaTestResult(null);
    try {
      const res = await fetch('https://bwjowttcu5lcrmpnbdl32mly2m0yejds.lambda-url.us-east-1.on.aws/');
      if (!res.ok) throw new Error('Lambda test failed');
      const data = await res.json();
      setLambdaTestResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <h1>News Digest Outcome Agent</h1>
      <hr style={{ margin: '30px 0' }} />
      <h2>Agent Task Demo</h2>
      <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
        <label>
          Task:
          <input value={task} onChange={e => setTask(e.target.value)} style={{ marginLeft: 8 }} />
        </label>
        <br />
        <label>
          Params (JSON):
          <input value={params} onChange={e => setParams(e.target.value)} style={{ marginLeft: 8, width: 200 }} />
        </label>
        <br />
        <button type="submit">Send to Agent</button>
      </form>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {result && (
        <div style={{ background: '#222', color: '#fff', padding: 10, borderRadius: 6 }}>
          <strong>Result:</strong>
          <pre style={{ color: '#0ff', background: 'inherit' }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      <hr style={{ margin: '30px 0' }} />
      <h2>Search Relevant Articles</h2>
      <form onSubmit={handleSearch} style={{ marginBottom: 20 }}>
        <label>
          Search (comma-separated keywords):
          <input value={search} onChange={e => setSearch(e.target.value)} style={{ marginLeft: 8, width: 220 }} />
        </label>
        <button type="submit" style={{ marginLeft: 8 }}>Search</button>
      </form>
      {searchResults.length > 0 && (
        <div style={{ background: '#222', color: '#fff', padding: 10, borderRadius: 6, marginBottom: 10 }}>
          <strong>Search Results:</strong>
          <ul>
            {searchResults.map((article, idx) => (
              <li key={article.id || idx}>
                <b>{article.title}</b> ({article.publishedDate}, {article.source})<br />
                {article.body && article.body.slice(0, 120)}{article.body && article.body.length > 120 ? '...' : ''}
              </li>
            ))}
          </ul>
        </div>
      )}
      <button onClick={testLambdaUrl} style={{ marginBottom: 20 }}>Test Lambda Function URL</button>
      {lambdaTestResult && (
        <div style={{ background: '#222', color: '#fff', padding: 10, borderRadius: 6, marginBottom: 10 }}>
          <strong>Lambda Test Result:</strong>
          <pre style={{ color: '#0ff', background: 'inherit' }}>{JSON.stringify(lambdaTestResult, null, 2)}</pre>
        </div>
      )}
    </>
  )
}

export default App
