import {
  BrowserRouter as Router,
  Routes,
  Route
} from 'react-router-dom';

import Analysis from './modules/analysis/Analysis';
import About from './modules/about/About';
import Layout from "./components/Layout";
import Dashboard from './modules/dashboard/Dashboard';
import Search from './modules/search/Search';

function App() {
  return (
    <Router>
      <Layout>
        <div className="w-full dark:bg-gray-950 bg-opacity-90 rounded-xl shadow-lg min-h-[80vh] flex flex-col">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/about" element={<About />} />
            <Route path="/search" element={<Search />} />
          </Routes>
        </div>
      </Layout>
    </Router>
  );
}

export default App;
