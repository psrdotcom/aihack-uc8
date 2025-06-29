import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const defaultData = [
  { name: 'A', uv: 1000, pv: 2400, amt: 2400 },
  { name: 'B', uv: 2000, pv: 1398, amt: 2210 },
  { name: 'C', uv: 1500, pv: 9800, amt: 2290 },
];

const Analysis: React.FC = () => {
  const [input, setInput] = useState('');
  const [data, setData] = useState(defaultData);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate search result based on input
    if (input.toLowerCase() === 'x') {
      setData([
        { name: 'X1', uv: 500, pv: 1200, amt: 1100 },
        { name: 'X2', uv: 800, pv: 1500, amt: 1300 },
      ]);
    } else if (input.toLowerCase() === 'y') {
      setData([
        { name: 'Y1', uv: 2000, pv: 3000, amt: 2500 },
        { name: 'Y2', uv: 1000, pv: 2000, amt: 1500 },
      ]);
    } else {
      setData(defaultData);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Analysis</h2>
      <form onSubmit={handleSearch} className="mb-6 flex gap-2">
        <input
          className="border rounded px-3 py-2 flex-1"
          placeholder="Type 'x' or 'y' to see different results"
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Search</button>
      </form>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded shadow p-4">
          <h3 className="font-semibold mb-2">Bar Chart</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="pv" fill="#8884d8" />
              <Bar dataKey="uv" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded shadow p-4">
          <h3 className="font-semibold mb-2">Line Chart</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="pv" stroke="#8884d8" />
              <Line type="monotone" dataKey="uv" stroke="#82ca9d" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Analysis;
