import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend,
  PieChart, Pie, Cell
} from 'recharts';
import {
  Users, ShoppingCart, DollarSign, TrendingUp,
  AlertCircle, Search, Calendar
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

function App() {
  const [data, setData] = useState({
    revenue: [],
    categories: [],
    topCustomers: [],
    regions: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Bonus: Filters State
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [revRes, catRes, custRes, regRes] = await Promise.all([
          fetch(`${API_BASE}/revenue`),
          fetch(`${API_BASE}/categories`),
          fetch(`${API_BASE}/top-customers`),
          fetch(`${API_BASE}/regions`)
        ]);

        if (!revRes.ok || !catRes.ok || !custRes.ok || !regRes.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        setData({
          revenue: await revRes.json(),
          categories: await catRes.json(),
          topCustomers: await custRes.json(),
          regions: await regRes.json()
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Bonus: Apply Filters
  const filteredCustomers = data.topCustomers.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.customer_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredRevenue = data.revenue.filter(r => {
    if (!dateRange.start && !dateRange.end) return true;
    const rDate = r.order_year_month;
    const afterStart = !dateRange.start || rDate >= dateRange.start;
    const beforeEnd = !dateRange.end || rDate <= dateRange.end;
    return afterStart && beforeEnd;
  });

  // Aggregated KPIs (computed from full data, not filtered data)
  const totalRevenue = data.regions.reduce((sum, r) => sum + r.total_revenue, 0);
  const totalCustomers = data.regions.reduce((sum, r) => sum + r.num_customers, 0);
  const totalOrders = data.regions.reduce((sum, r) => sum + r.num_orders, 0);
  const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-6 max-w-md w-full text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-red-400 mb-2">Failed to load data</h2>
          <p className="text-slate-400">{error}</p>
          <p className="text-sm text-slate-500 mt-4">Make sure the Python backend is running on port 8000.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 font-sans">
      <header className="sticky top-0 z-10 bg-slate-800 border-b border-slate-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
                E
              </div>
              <h1 className="text-xl font-semibold tracking-tight text-white">Ecommerce Pulse</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KpiCard title="Total Revenue" value={`$${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} icon={DollarSign} color="indigo" loading={loading} />
          <KpiCard title="Total Orders" value={totalOrders.toLocaleString()} icon={ShoppingCart} color="emerald" loading={loading} />
          <KpiCard title="Active Customers" value={totalCustomers.toLocaleString()} icon={Users} color="blue" loading={loading} />
          <KpiCard title="Avg Order Value" value={`$${avgOrderValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} icon={TrendingUp} color="amber" loading={loading} />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm min-h-[400px] flex flex-col">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-400" />
                Monthly Revenue Trend
              </h2>
              <div className="flex items-center gap-2 text-sm bg-slate-900/50 p-1.5 rounded-lg border border-slate-700">
                <Calendar className="w-4 h-4 text-slate-400 ml-2" />
                <input
                  type="month"
                  value={dateRange.start}
                  onChange={e => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                  className="bg-transparent text-slate-300 border-none outline-none focus:ring-0 ml-1 py-1"
                />
                <span className="text-slate-500">—</span>
                <input
                  type="month"
                  value={dateRange.end}
                  onChange={e => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                  className="bg-transparent text-slate-300 border-none outline-none focus:ring-0 mr-1 py-1"
                />
              </div>
            </div>

            <div className="flex-1 min-h-[300px]">
              {loading ? <Skeleton /> : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={filteredRevenue} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="order_year_month" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} tickMargin={10} />
                    <YAxis
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8' }}
                      tickFormatter={(value) => `$${value >= 1000 ? (value / 1000).toFixed(0) + 'k' : value}`}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }}
                      itemStyle={{ color: '#818cf8' }}
                      formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
                    />
                    <Line type="monotone" dataKey="total_revenue" stroke="#818cf8" strokeWidth={3} dot={{ r: 4, fill: '#818cf8', strokeWidth: 0 }} activeDot={{ r: 6, fill: '#6366f1' }} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm min-h-[400px] flex flex-col">
            <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-emerald-400" />
              Revenue by Category
            </h2>
            <div className="flex-1 min-h-[300px]">
              {loading ? <Skeleton /> : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={data.categories}
                      dataKey="total_revenue"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                    >
                      {data.categories.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }}
                      formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
                    />
                    <Legend verticalAlign="bottom" height={36} iconType="circle" />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Row: Top Customers & Regions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 shadow-sm overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-400" />
                Top Customers
              </h2>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search customers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-slate-900/50 border border-slate-700 text-sm rounded-lg block w-full pl-9 pr-3 py-2 outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              {loading ? (
                <div className="p-6"><Skeleton /></div>
              ) : (
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-slate-900/50 text-slate-400 uppercase text-xs">
                    <tr>
                      <th className="px-6 py-4 font-medium tracking-wider">Customer</th>
                      <th className="px-6 py-4 font-medium tracking-wider">Region</th>
                      <th className="px-6 py-4 font-medium tracking-wider text-right">Total Spend</th>
                      <th className="px-6 py-4 font-medium tracking-wider text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {filteredCustomers.length > 0 ? filteredCustomers.map((cust) => (
                      <tr key={cust.customer_id} className="hover:bg-slate-700/50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex flex-col">
                            <span className="font-medium text-slate-200">{cust.name}</span>
                            <span className="text-xs text-slate-500">{cust.customer_id}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-slate-300">{cust.region}</td>
                        <td className="px-6 py-4 text-right font-medium text-slate-200">
                          ${cust.total_spend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cust.churned ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            }`}>
                            {cust.churned ? 'Churned' : 'Active'}
                          </span>
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan="4" className="px-6 py-8 text-center text-slate-500">
                          No customers found matching "{searchQuery}"
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 shadow-sm overflow-hidden flex flex-col">
            <div className="p-6 border-b border-slate-700">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-amber-400" />
                Region Performance
              </h2>
            </div>
            <div className="p-6 flex-1 flex flex-col justify-center">
              {loading ? <Skeleton /> : (
                <div className="space-y-6">
                  {data.regions.map((region, idx) => (
                    <div key={region.region}>
                      <div className="flex justify-between items-end mb-2">
                        <span className="font-medium text-slate-200">{region.region}</span>
                        <span className="text-sm font-semibold text-indigo-400">
                          ${(region.total_revenue / 1000).toFixed(1)}k
                        </span>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-2">
                        <div
                          className="bg-indigo-500 h-2 rounded-full"
                          style={{ width: `${(region.total_revenue / totalRevenue) * 100}%` }}
                        />
                      </div>
                      <div className="flex justify-between mt-1 text-xs text-slate-500">
                        <span>{region.num_customers} customers</span>
                        <span>{region.num_orders} orders</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}

// Subcomponents
function KpiCard({ title, value, icon: Icon, color, loading }) {
  const colorMap = {
    indigo: 'text-indigo-400 bg-indigo-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    blue: 'text-blue-400 bg-blue-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm relative overflow-hidden group">
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          {loading ? (
            <div className="h-8 w-32 bg-slate-700 rounded animate-pulse mt-2" />
          ) : (
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${colorMap[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

function Skeleton() {
  return (
    <div className="w-full h-full min-h-[200px] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4 text-slate-500">
        <svg className="w-10 h-10 animate-spin text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      </div>
    </div>
  );
}

export default App;
