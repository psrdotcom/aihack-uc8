import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, BarChart2, Info, Menu } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: <Home className="w-5 h-5" /> },
  { to: '/analysis', label: 'Analysis', icon: <BarChart2 className="w-5 h-5" /> },
  { to: '/about', label: 'About', icon: <Info className="w-5 h-5" /> },
];

const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={`h-screen fixed left-0 top-0 z-30 bg-gray-900 border-r border-gray-800 flex flex-col transition-all duration-300 shadow-lg ${collapsed ? 'w-16' : 'w-56'}`}
      style={{ minWidth: collapsed ? '4rem' : '14rem' }}
    >
      <button
        className="m-2 mb-4 p-2 rounded bg-gray-800 hover:bg-gray-700 transition-colors flex items-center justify-center text-lg focus:outline-none"
        onClick={() => setCollapsed((c) => !c)}
        aria-label="Toggle sidebar"
        type="button"
      >
        <Menu className="w-6 h-6" />
      </button>
      <nav className="flex-1 flex flex-col gap-2">
        {navItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={`flex items-center gap-3 px-4 py-3 rounded transition-colors duration-200 hover:bg-gray-800 text-base font-medium ${location.pathname === item.to ? 'bg-gray-800 font-bold' : ''} ${collapsed ? 'justify-center px-2' : ''}`}
            title={collapsed ? item.label : undefined}
          >
            {item.icon}
            {!collapsed && item.label}
            {collapsed && <span className="sr-only">{item.label}</span>}
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
