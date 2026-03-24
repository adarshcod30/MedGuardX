'use client';
import { motion } from 'framer-motion';
import { LogIn, UserPlus, Shield, AlertCircle, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/lib/api';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const roles = [
  { value: 'doctor', label: 'Doctor', emoji: '🩺', desc: 'Full treatment access' },
  { value: 'nurse', label: 'Nurse', emoji: '👩‍⚕️', desc: 'Partial clinical access' },
  { value: 'researcher', label: 'Researcher', emoji: '🔬', desc: 'Anonymized data only' },
  { value: 'patient', label: 'Patient', emoji: '🧑', desc: 'Own records access' },
  { value: 'company', label: 'Company', emoji: '🏢', desc: 'Restricted access' },
];

export default function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('doctor');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const isLoggedIn = typeof window !== 'undefined' && localStorage.getItem('medguardx_token');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      let res;
      if (mode === 'login') {
        res = await api.login(username, password);
      } else {
        res = await api.register(username, password, role, fullName);
      }
      localStorage.setItem('medguardx_token', res.access_token);
      localStorage.setItem('medguardx_role', res.role);
      localStorage.setItem('medguardx_user', res.username);
      setSuccess(`Welcome, ${res.username}! Role: ${res.role}`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('medguardx_token');
    localStorage.removeItem('medguardx_role');
    localStorage.removeItem('medguardx_user');
    setSuccess('');
    window.location.reload();
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="max-w-lg mx-auto space-y-6 pt-8">
      <motion.div variants={item} className="text-center">
        <div className="inline-flex p-3 rounded-2xl bg-primary-50 mb-4">
          <Shield className="w-10 h-10 text-primary-600" />
        </div>
        <h1 className="text-2xl font-bold text-surface-900">MedGuard<span className="text-primary-600">X</span> Auth</h1>
        <p className="text-surface-500 mt-1">Secure access with role-based authentication</p>
      </motion.div>

      {/* Mode Toggle */}
      <motion.div variants={item} className="flex p-1 rounded-xl bg-surface-100">
        {[
          { key: 'login', label: 'Sign In', icon: LogIn },
          { key: 'register', label: 'Register', icon: UserPlus },
        ].map(m => (
          <button key={m.key} onClick={() => { setMode(m.key as any); setError(''); setSuccess(''); }}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all
              ${mode === m.key ? 'bg-white text-primary-700 shadow-sm' : 'text-surface-500 hover:text-surface-700'}`}
          >
            <m.icon className="w-4 h-4" /> {m.label}
          </button>
        ))}
      </motion.div>

      {/* Form */}
      <motion.form variants={item} onSubmit={handleSubmit} className="glass-card-solid p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-surface-700 mb-1.5">Username</label>
          <input value={username} onChange={e => setUsername(e.target.value)} required
            placeholder="Enter username" className="input-field" />
        </div>
        <div>
          <label className="block text-sm font-medium text-surface-700 mb-1.5">Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
            placeholder="Enter password" className="input-field" />
        </div>

        {mode === 'register' && (
          <>
            <div>
              <label className="block text-sm font-medium text-surface-700 mb-1.5">Full Name</label>
              <input value={fullName} onChange={e => setFullName(e.target.value)}
                placeholder="Dr. Full Name" className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-700 mb-2">Select Role</label>
              <div className="grid grid-cols-2 gap-2">
                {roles.map(r => (
                  <motion.button key={r.value} type="button" whileTap={{ scale: 0.97 }}
                    onClick={() => setRole(r.value)}
                    className={`p-3 rounded-xl text-left transition-all border
                      ${role === r.value
                        ? 'bg-primary-50 border-primary-300 ring-2 ring-primary-200'
                        : 'bg-surface-50 border-surface-200 hover:border-surface-300'}`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{r.emoji}</span>
                      <span className="text-sm font-semibold text-surface-800">{r.label}</span>
                    </div>
                    <p className="text-xs text-surface-400 mt-0.5 ml-7">{r.desc}</p>
                  </motion.button>
                ))}
              </div>
            </div>
          </>
        )}

        {error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex items-center gap-2 p-3 rounded-xl bg-red-50 text-red-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
          </motion.div>
        )}

        {success && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex items-center gap-2 p-3 rounded-xl bg-emerald-50 text-emerald-700 text-sm">
            <CheckCircle className="w-4 h-4 flex-shrink-0" /> {success}
          </motion.div>
        )}

        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
          type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
          {loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </motion.button>

        {isLoggedIn && (
          <button type="button" onClick={handleLogout}
            className="btn-secondary w-full text-red-600 hover:bg-red-50">
            Sign Out
          </button>
        )}
      </motion.form>

      {/* RBAC Info */}
      <motion.div variants={item} className="glass-card-solid p-5">
        <h3 className="text-sm font-semibold text-surface-600 mb-3">Role-Based Access Control</h3>
        <div className="space-y-2 text-xs">
          {[
            { role: 'Doctor', access: 'Full data with consent', color: 'bg-blue-50 text-blue-700' },
            { role: 'Nurse', access: 'Partial — identifiers masked', color: 'bg-teal-50 text-teal-700' },
            { role: 'Researcher', access: 'Fully anonymized data', color: 'bg-violet-50 text-violet-700' },
            { role: 'Patient', access: 'Own records only', color: 'bg-emerald-50 text-emerald-700' },
            { role: 'Company', access: 'Heavily restricted', color: 'bg-amber-50 text-amber-700' },
          ].map(r => (
            <div key={r.role} className={`flex justify-between px-3 py-2 rounded-lg ${r.color}`}>
              <span className="font-medium">{r.role}</span>
              <span>{r.access}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
