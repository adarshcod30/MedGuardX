'use client';
import { motion } from 'framer-motion';
import { Shield, Database, Eye, FileText, Upload, Activity, Users, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

interface Stats {
  total_patients: number;
  total_records: number;
  total_access_events: number;
  total_audit_logs: number;
  recent_uploads: number;
  recent_accesses: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.stats().then(setStats).catch(() => {
      setStats({ total_patients: 0, total_records: 0, total_access_events: 0, total_audit_logs: 0, recent_uploads: 0, recent_accesses: 0 });
    }).finally(() => setLoading(false));
  }, []);

  const statCards = stats ? [
    { label: 'Total Patients', value: stats.total_patients, icon: Users, color: 'from-primary-500 to-primary-600', bgLight: 'bg-primary-50', textColor: 'text-primary-600' },
    { label: 'Stored Records', value: stats.total_records, icon: Database, color: 'from-accent-teal to-emerald-500', bgLight: 'bg-teal-50', textColor: 'text-teal-600' },
    { label: 'Access Events', value: stats.total_access_events, icon: Eye, color: 'from-accent-amber to-orange-500', bgLight: 'bg-amber-50', textColor: 'text-amber-600' },
    { label: 'Audit Logs', value: stats.total_audit_logs, icon: FileText, color: 'from-accent-rose to-pink-500', bgLight: 'bg-rose-50', textColor: 'text-rose-600' },
    { label: 'Uploads (7d)', value: stats.recent_uploads, icon: Upload, color: 'from-accent-sky to-blue-500', bgLight: 'bg-sky-50', textColor: 'text-sky-600' },
    { label: 'Accesses (7d)', value: stats.recent_accesses, icon: Activity, color: 'from-violet-500 to-purple-500', bgLight: 'bg-violet-50', textColor: 'text-violet-600' },
  ] : [];

  const features = [
    { icon: '🔐', title: 'AES Encryption', desc: 'All data encrypted at rest with military-grade encryption' },
    { icon: '🤖', title: 'AI PII Detection', desc: 'Microsoft Presidio-powered NLP entity recognition' },
    { icon: '🎭', title: 'Context-Aware Masking', desc: 'Dynamic masking based on role, purpose & consent' },
    { icon: '📋', title: 'Legal Compliance', desc: 'DPDP Bill, IT Act, GDPR principles enforced' },
    { icon: '🏥', title: 'HL7 Support', desc: 'Parse and protect structured healthcare messages' },
    { icon: '📊', title: 'Full Audit Trail', desc: 'Every access logged with policy explainability' },
  ];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-8">
      {/* Hero Section */}
      <motion.div variants={item} className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-500 to-indigo-400 p-8 md:p-10 text-white">
        <div className="absolute top-0 right-0 w-80 h-80 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/3 blur-3xl" />
        <div className="absolute bottom-0 left-0 w-60 h-60 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/3 blur-2xl" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 rounded-xl bg-white/20 backdrop-blur-sm">
              <Shield className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">MedGuard<span className="text-primary-200">X</span></h1>
              <p className="text-primary-200 text-sm">Healthcare Data Protection System</p>
            </div>
          </div>
          <p className="text-lg text-white/80 max-w-2xl leading-relaxed">
            AI-powered data protection with context-aware masking, role-based access control, 
            and full legal compliance for healthcare data across HL7, PDF, images, and text.
          </p>
          <div className="flex gap-3 mt-6">
            <motion.a whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} href="/upload"
              className="px-6 py-2.5 bg-white text-primary-700 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all">
              Upload Data
            </motion.a>
            <motion.a whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} href="/preview"
              className="px-6 py-2.5 bg-white/15 backdrop-blur-sm text-white border border-white/25 rounded-xl font-medium hover:bg-white/25 transition-all">
              Try Live Preview
            </motion.a>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={item} className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((s, i) => (
          <motion.div
            key={s.label}
            variants={item}
            whileHover={{ y: -4, boxShadow: '0 12px 40px rgba(0,0,0,0.1)' }}
            className="stat-card group cursor-default"
          >
            <div className={`w-10 h-10 rounded-xl ${s.bgLight} flex items-center justify-center mb-3 
              group-hover:scale-110 transition-transform duration-300`}>
              <s.icon className={`w-5 h-5 ${s.textColor}`} />
            </div>
            <p className="text-2xl font-bold text-surface-900">
              {loading ? '—' : <AnimatedCounter value={s.value} />}
            </p>
            <p className="text-xs text-surface-400 mt-1">{s.label}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Features Grid */}
      <motion.div variants={item}>
        <h2 className="text-xl font-semibold text-surface-800 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-500" />
          Core Capabilities
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              variants={item}
              whileHover={{ y: -2 }}
              className="glass-card-solid p-5 hover:shadow-glass-lg transition-all duration-300 group"
            >
              <span className="text-2xl mb-3 block group-hover:scale-110 transition-transform">{f.icon}</span>
              <h3 className="font-semibold text-surface-800">{f.title}</h3>
              <p className="text-sm text-surface-500 mt-1 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Architecture Flow */}
      <motion.div variants={item} className="glass-card-solid p-6">
        <h2 className="text-lg font-semibold text-surface-800 mb-5">System Pipeline</h2>
        <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
          {[
            { label: 'Data Upload', color: 'bg-blue-100 text-blue-700' },
            { label: 'Type Detection', color: 'bg-indigo-100 text-indigo-700' },
            { label: 'Text Extraction', color: 'bg-violet-100 text-violet-700' },
            { label: 'PII Scan', color: 'bg-purple-100 text-purple-700' },
            { label: 'Encryption', color: 'bg-pink-100 text-pink-700' },
            { label: 'Secure Storage', color: 'bg-rose-100 text-rose-700' },
            { label: 'Policy Engine', color: 'bg-amber-100 text-amber-700' },
            { label: 'Dynamic Masking', color: 'bg-teal-100 text-teal-700' },
            { label: 'Audit Log', color: 'bg-emerald-100 text-emerald-700' },
          ].map((step, i, arr) => (
            <div key={step.label} className="flex items-center gap-2">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: i * 0.1 }}
                className={`px-3 py-1.5 rounded-lg font-medium ${step.color}`}
              >
                {step.label}
              </motion.div>
              {i < arr.length - 1 && (
                <span className="text-surface-300 text-lg">→</span>
              )}
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}

function AnimatedCounter({ value }: { value: number }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (value === 0) return;
    const duration = 1000;
    const steps = 30;
    const increment = value / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [value]);
  return <>{count}</>;
}
