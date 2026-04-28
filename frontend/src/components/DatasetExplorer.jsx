import React, { useState } from 'react';
import { Search, Filter, ArrowUpDown, Database, UploadCloud } from 'lucide-react';

// NOTE: This component defines the UI structure for the Dataset Explorer.
// Backend/Supabase logic should be wired up by passing appropriate props/hooks.

const DatasetExplorer = ({ 
  data = [], 
  columns = [], 
  onUpload, 
  isUploading = false 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // UI-only Sorting Logic
  const sortedData = React.useMemo(() => {
    let sortableItems = [...data];
    if (sortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [data, sortConfig]);

  // UI-only Search Logic
  const filteredData = React.useMemo(() => {
    return sortedData.filter(item => {
      return Object.values(item).some(val => 
        String(val).toLowerCase().includes(searchTerm.toLowerCase())
      );
    });
  }, [sortedData, searchTerm]);

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  return (
    <div className="dataset-explorer">
      {/* 1. Upload & Storage Section */}
      <div className="explorer-header glass-card">
        <div>
          <h2>Dataset Explorer</h2>
          <p className="text-muted" style={{ marginTop: '8px' }}>
            Upload and inspect data stored in Supabase before running fairness analysis.
          </p>
        </div>
        <button className="btn" onClick={onUpload} disabled={isUploading}>
          <UploadCloud size={18} />
          {isUploading ? "Uploading to Supabase..." : "Upload New CSV"}
        </button>
      </div>

      {/* 2. Search & Filter Controls */}
      <div className="controls-bar">
        <div className="search-input-wrapper">
          <Search size={18} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search across all rows..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <button className="btn-outline" style={{ padding: '14px 24px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={18} /> Filters
        </button>
      </div>

      {/* 3. Clean Table Format with Sorting */}
      <div className="table-container glass-card">
        {data.length === 0 ? (
          <div className="empty-state">
            <Database size={48} className="text-muted" style={{ marginBottom: '16px' }} />
            <p className="text-muted">No dataset loaded. Upload a CSV to begin.</p>
          </div>
        ) : (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    {columns.map((col) => (
                      <th key={col} onClick={() => requestSort(col)} className="sortable-header">
                        <div className="header-content">
                          {col}
                          <ArrowUpDown size={14} className="sort-icon text-muted" />
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map((row, idx) => (
                    <tr key={idx}>
                      {columns.map((col) => (
                        <td key={col}>{row[col]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-footer">
              <p className="text-muted">Total records: {filteredData.length} {searchTerm && '(Filtered)'}</p>
            </div>
          </>
        )}
      </div>

      {/* Inline Styles specifically for this component to maintain modularity */}
      <style>{`
        .dataset-explorer { display: grid; gap: 32px; animation: fadeIn 0.4s ease-out; }
        .explorer-header { display: flex; justify-content: space-between; align-items: center; padding: 32px 48px; border-radius: 28px; }
        .controls-bar { display: flex; gap: 16px; align-items: center; }
        .search-input-wrapper { position: relative; flex: 1; }
        .search-icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--text-secondary); }
        .search-input { width: 100%; background: var(--bg-panel); border: 1px solid var(--border); padding: 14px 16px 14px 48px; border-radius: 12px; color: white; font-size: 15px; outline: none; transition: border-color 0.2s; }
        .search-input:focus { border-color: var(--primary); }
        .table-container { padding: 0; border-radius: 28px; overflow: hidden; }
        .data-table { width: 100%; border-collapse: collapse; text-align: left; }
        .data-table th { background: rgba(0,0,0,0.2); padding: 20px 24px; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.2s; }
        .data-table th:hover { background: rgba(255,255,255,0.05); color: white; }
        .header-content { display: flex; align-items: center; gap: 8px; }
        .data-table td { padding: 16px 24px; border-bottom: 1px solid rgba(255,255,255,0.02); font-size: 14px; white-space: nowrap; }
        .data-table tr:hover td { background: rgba(255,255,255,0.02); }
        .empty-state { padding: 100px; text-align: center; display: flex; flex-direction: column; align-items: center; }
        .table-footer { padding: 16px 24px; border-top: 1px solid var(--border); text-align: center; font-size: 13px; }
      `}</style>
    </div>
  );
};

export default DatasetExplorer;
