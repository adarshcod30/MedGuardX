'use client';
import { motion } from 'framer-motion';
import { FileText, Clock, User, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const actionColors: Record<string, string> = {
  UPLOAD: 'bg-blue-100 text-blue-700',
  RETRIEVE: 'bg-emerald-100 text-emerald-700',
  ACCESS_DENIED: 'bg-red-100 text-red-700',
  PREVIEW: 'bg-violet-100 text-violet-700',
};

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const pageSize = 15;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.audit(pageSize, page * pageSize);
      setLogs(res.logs || []);
      setTotal(res.total || 0);
    } catch { setLogs([]); }
    setLoading(false);
  };

  useEffect(() => { fetchLogs(); }, [page]);

  const filtered = filter
    ? logs.filter(l => l.action?.toLowerCase().includes(filter.toLowerCase()) ||
        l.details?.toLowerCase().includes(filter.toLowerCase()))
    : logs;

  const totalPages = Math.ceil(total / pageSize);

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 flex items-center gap-2">
            <FileText className="w-6 h-6 text-primary-500" /> Audit Logs
          </h1>
          <p className="text-surface-500 mt-1">Complete trail of all data access events</p>
        </div>
        <span className="badge bg-primary-100 text-primary-700">{total} total events</span>
      </motion.div>

      {/* Filter */}
      <motion.div variants={item} className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input value={filter} onChange={e => setFilter(e.target.value)}
            placeholder="Filter logs..." className="input-field pl-10" />
        </div>
        <motion.button whileTap={{ scale: 0.97 }} onClick={fetchLogs} className="btn-secondary">
          Refresh
        </motion.button>
      </motion.div>

      {/* Table */}
      <motion.div variants={item} className="glass-card-solid overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-50 border-b border-surface-200">
                <th className="px-5 py-3 text-left font-semibold text-surface-500">Action</th>
                <th className="px-5 py-3 text-left font-semibold text-surface-500">Actor</th>
                <th className="px-5 py-3 text-left font-semibold text-surface-500">Target</th>
                <th className="px-5 py-3 text-left font-semibold text-surface-500">Details</th>
                <th className="px-5 py-3 text-left font-semibold text-surface-500">Time</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-surface-100">
                    {[...Array(5)].map((_, j) => (
                      <td key={j} className="px-5 py-4">
                        <div className="h-4 bg-surface-100 rounded animate-pulse w-24"></div>
                      </td>
                    ))}
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-12 text-center text-surface-400">
                    No audit logs found
                  </td>
                </tr>
              ) : (
                filtered.map((log, i) => (
                  <motion.tr
                    key={log.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="border-b border-surface-100 hover:bg-surface-50 transition-colors"
                  >
                    <td className="px-5 py-3.5">
                      <span className={`badge ${actionColors[log.action] || 'bg-surface-100 text-surface-700'}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="flex items-center gap-1.5 text-surface-700">
                        <User className="w-3.5 h-3.5 text-surface-400" />
                        {log.actor || '—'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-mono text-xs text-surface-600 bg-surface-100 px-2 py-0.5 rounded">
                        {log.target ? log.target.substring(0, 12) + '...' : '—'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-surface-600 max-w-xs truncate">{log.details || '—'}</td>
                    <td className="px-5 py-3.5">
                      <span className="flex items-center gap-1.5 text-surface-500 text-xs">
                        <Clock className="w-3.5 h-3.5" />
                        {log.timestamp}
                      </span>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-surface-200 bg-surface-50">
            <span className="text-xs text-surface-400">
              Page {page + 1} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
                className="p-1.5 rounded-lg hover:bg-surface-200 disabled:opacity-30 transition-colors">
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}
                className="p-1.5 rounded-lg hover:bg-surface-200 disabled:opacity-30 transition-colors">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
