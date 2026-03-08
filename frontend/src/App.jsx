import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 font-sans">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-slate-800 border-b border-slate-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
                E
              </div>
              <h1 className="text-xl font-semibold tracking-tight text-white">Ecommerce Pulse</h1>
            </div>
            <div className="text-sm font-medium text-slate-400 bg-slate-800/50 py-1.5 px-3 rounded-full border border-slate-700">
              Live Dashboard
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        {/* KPI Cards Placeholder */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="h-4 w-24 bg-slate-700 rounded animate-pulse mb-4" />
              <div className="h-8 w-32 bg-slate-600 rounded animate-pulse" />
            </div>
          ))}
        </div>

        {/* Charts Grid Placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm min-h-[400px] flex items-center justify-center">
            <div className="flex flex-col items-center gap-4 text-slate-500">
              <svg className="w-12 h-12 animate-spin text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span className="font-medium">Loading Revenue Trend...</span>
            </div>
          </div>
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm min-h-[400px] flex items-center justify-center">
            <div className="flex flex-col items-center gap-4 text-slate-500">
              <svg className="w-12 h-12 animate-spin text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span className="font-medium">Loading Categories...</span>
            </div>
          </div>
        </div>

        {/* Table Placeholder */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-sm min-h-[500px] flex items-center justify-center">
          <div className="flex flex-col items-center gap-4 text-slate-500">
            <svg className="w-12 h-12 animate-spin text-slate-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span className="font-medium">Loading Customer Data...</span>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
