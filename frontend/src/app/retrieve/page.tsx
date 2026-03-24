'use client';
import { motion } from 'framer-motion';
import { Search, Shield, User, Briefcase, CheckCircle, XCircle, Lock, Unlock } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/lib/api';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const roles = ['doctor', 'nurse', 'researcher', 'patient', 'company'];
const purposes = ['treatment', 'research', 'billing', 'legal', 'personal'];

const roleColors: Record<string, string> = {
  doctor: 'bg-blue-100 text-blue-700 border-blue-200',
  nurse: 'bg-teal-100 text-teal-700 border-teal-200',
  researcher: 'bg-violet-100 text-violet-700 border-violet-200',
  patient: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  company: 'bg-amber-100 text-amber-700 border-amber-200',
};

const strategyStyles: Record<string, { bg: string; icon: any; label: string }> = {
  full_access: { bg: 'bg-emerald-50 border-emerald-300', icon: Unlock, label: 'Full Access' },
  partial_mask: { bg: 'bg-amber-50 border-amber-300', icon: Shield, label: 'Partial Masking' },
  full_anonymize: { bg: 'bg-red-50 border-red-300', icon: Lock, label: 'Fully Anonymized' },
  deny: { bg: 'bg-red-100 border-red-400', icon: XCircle, label: 'Access Denied' },
};

export default function RetrievePage() {
  const [patientId, setPatientId] = useState('');
  const [role, setRole] = useState('doctor');
  const [purpose, setPurpose] = useState('treatment');
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [activeRecordId, setActiveRecordId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRetrieve = async () => {
    if (!patientId.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    setActiveRecordId(null);
    try {
      const res = await api.retrieve(patientId, role, purpose, consent);
      setResult(res);
      if (res.records && res.records.length > 0) {
        setActiveRecordId(res.records[0].id);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const sStyle = result ? strategyStyles[result.masking_strategy] : null;

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <h1 className="text-2xl font-bold text-surface-900">Retrieve Data</h1>
        <p className="text-surface-500 mt-1">Access patient data with context-aware masking</p>
      </motion.div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* Form */}
        <motion.div variants={item} className="lg:col-span-2 glass-card-solid p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-surface-700 mb-1.5">Patient ID</label>
            <input value={patientId} onChange={e => setPatientId(e.target.value)}
              placeholder="Enter patient UUID" className="input-field font-mono text-sm" />
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-700 mb-2">Role</label>
            <div className="flex flex-wrap gap-2">
              {roles.map(r => (
                <motion.button key={r} whileTap={{ scale: 0.95 }}
                  onClick={() => setRole(r)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all capitalize
                    ${role === r ? roleColors[r] + ' ring-2 ring-offset-1 ring-primary-300' : 'bg-surface-50 text-surface-500 border-surface-200 hover:bg-surface-100'}`}
                >
                  {r}
                </motion.button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-surface-700 mb-2">Purpose</label>
            <div className="flex flex-wrap gap-2">
              {purposes.map(p => (
                <motion.button key={p} whileTap={{ scale: 0.95 }}
                  onClick={() => setPurpose(p)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all capitalize
                    ${purpose === p ? 'bg-primary-50 text-primary-700 border-primary-200 ring-2 ring-offset-1 ring-primary-300' : 'bg-surface-50 text-surface-500 border-surface-200 hover:bg-surface-100'}`}
                >
                  {p}
                </motion.button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-surface-50">
            <span className="text-sm font-medium text-surface-700">Patient Consent</span>
            <motion.button whileTap={{ scale: 0.9 }}
              onClick={() => setConsent(!consent)}
              className={`w-12 h-6 rounded-full transition-all duration-300 relative
                ${consent ? 'bg-emerald-500' : 'bg-surface-300'}`}
            >
              <motion.div animate={{ x: consent ? 24 : 2 }}
                className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm" />
            </motion.button>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleRetrieve}
            disabled={loading || !patientId.trim()}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}
                className="w-5 h-5 rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <><Search className="w-4 h-4" /> Retrieve Data</>
            )}
          </motion.button>
        </motion.div>

        {/* Result */}
        <motion.div variants={item} className="lg:col-span-3 space-y-4">
          {error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="glass-card-solid p-5 border-l-4 border-red-500">
              <p className="text-red-700 font-medium flex items-center gap-2">
                <XCircle className="w-5 h-5" /> {error}
              </p>
            </motion.div>
          )}

          {result && (
            <>
              {/* Strategy Badge */}
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-xl border-2 ${sStyle?.bg} flex items-center gap-3`}
              >
                {sStyle && <sStyle.icon className="w-6 h-6" />}
                <div>
                  <p className="font-semibold">{sStyle?.label}</p>
                  <p className="text-sm opacity-75">{result.policy_rule}</p>
                </div>
                <span className="ml-auto badge bg-surface-800 text-white">{result.entities_masked} masked</span>
              </motion.div>

              {/* Masked Data */}
              {result.records && result.records.length > 0 ? (
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {result.records.map((rec: any, idx: number) => (
                      <button
                        key={rec.id}
                        onClick={() => setActiveRecordId(rec.id)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors
                          ${activeRecordId === rec.id ? 'bg-primary-500 text-white border-primary-600 shadow-sm' 
                          : 'bg-surface-50 text-surface-600 border-surface-200 hover:bg-surface-100 hover:text-surface-800'}`}
                      >
                        Record #{idx + 1} <span className="text-xs opacity-75 uppercase ml-1">({rec.file_type})</span>
                      </button>
                    ))}
                  </div>

                  {result.records.filter((r: any) => r.id === activeRecordId).map((activeRec: any) => (
                    <motion.div key={activeRec.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                      className="glass-card-solid p-6">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="text-sm font-semibold text-surface-500">Masked Output</h3>
                        <span className="text-xs bg-surface-100 text-surface-400 px-2 py-1 rounded-md max-w-xs truncate" title={activeRec.filename}>
                          {activeRec.filename}
                        </span>
                      </div>
                      <pre className="bg-surface-50 rounded-xl p-4 text-sm text-surface-800 whitespace-pre-wrap 
                        font-mono leading-relaxed max-h-96 overflow-y-auto border border-surface-200">
                        {activeRec.masked_content}
                      </pre>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <motion.div className="glass-card-solid p-6 text-center text-surface-500">
                  No records stored for this patient.
                </motion.div>
              )}
            </>
          )}

          {!result && !error && (
            <div className="glass-card-solid p-12 text-center">
              <Search className="w-12 h-12 text-surface-300 mx-auto mb-4" />
              <p className="text-surface-400">Enter a patient ID and your context to retrieve masked data</p>
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}
