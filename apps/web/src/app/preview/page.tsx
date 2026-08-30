'use client';
import { motion } from 'framer-motion';
import { Eye, Zap, ShieldAlert, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/lib/api';
import { useSession } from '@/lib/useSession';
import SignInPrompt from '@/components/SignInPrompt';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const entityColors: Record<string, string> = {
  PERSON: 'bg-blue-100 text-blue-700',
  PHONE_NUMBER: 'bg-amber-100 text-amber-700',
  EMAIL_ADDRESS: 'bg-teal-100 text-teal-700',
  LOCATION: 'bg-purple-100 text-purple-700',
  CREDIT_CARD: 'bg-red-100 text-red-700',
  IN_AADHAAR: 'bg-orange-100 text-orange-700',
  IN_PAN: 'bg-indigo-100 text-indigo-700',
  MEDICAL_RECORD_NUMBER: 'bg-cyan-100 text-cyan-700',
  IBAN_CODE: 'bg-red-100 text-red-700',
  IP_ADDRESS: 'bg-slate-100 text-slate-700',
  DEFAULT: 'bg-gray-100 text-gray-700',
};

const purposes = ['treatment', 'research', 'billing', 'legal', 'personal'];

const sampleTexts = [
  {
    label: '🏥 Patient Record',
    text: `Patient Name: Dr. Rajesh Kumar Sharma
Phone: +91-9876543210
Email: rajesh.sharma@hospital.org
Aadhaar: 2341 2341 2346
Address: 42, MG Road, Bangalore, Karnataka 560001
Diagnosis: Type-2 Diabetes Mellitus with hypertension
Insurance ID: STAR-HEALTH-2024-889922`,
  },
  {
    label: '📋 Discharge Summary',
    text: `Patient: Priya Patel (Female, 34 years)
MRN: MH-2024-55891
Contact: priya.patel@gmail.com | 8899776655
PAN: ABCDE1234F
Card: 4111 1111 1111 1111
Treating Doctor: Dr. Ananya Mehta
Hospital: Apollo Hospitals, Chennai
Diagnosis: Acute appendicitis — Laparoscopic appendectomy performed`,
  },
];

export default function PreviewPage() {
  const session = useSession();
  const [inputText, setInputText] = useState(sampleTexts[0].text);
  const [purpose, setPurpose] = useState('research');
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePreview = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.preview(inputText, purpose, consent);
      setResult(res);
    } catch (e: any) {
      setResult(null);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (session.ready && !session.loggedIn) {
    return <SignInPrompt action="preview masking" />;
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <h1 className="text-2xl font-bold text-surface-900 flex items-center gap-2">
          <Eye className="w-6 h-6 text-primary-500" /> Mask Preview
        </h1>
        <p className="text-surface-500 mt-1">
          Live PII masking as <span className="font-semibold capitalize text-primary-600">{session.role || '...'}</span> —
          masking reflects your signed-in role, chosen purpose, and consent.
        </p>
      </motion.div>

      {/* Sample Selector */}
      <motion.div variants={item} className="flex gap-3 flex-wrap">
        {sampleTexts.map((s, i) => (
          <motion.button key={i} whileTap={{ scale: 0.97 }}
            onClick={() => { setInputText(s.text); setResult(null); }}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all
              ${inputText === s.text ? 'bg-primary-100 text-primary-700 ring-2 ring-primary-300' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}
          >
            {s.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Role (read-only) + Purpose + Consent + Button */}
      <motion.div variants={item} className="flex items-center gap-3 flex-wrap">
        <span className="badge bg-primary-600 text-white capitalize">Role: {session.role}</span>
        <span className="text-sm font-medium text-surface-600 ml-2">Purpose:</span>
        {purposes.map(p => (
          <motion.button key={p} whileTap={{ scale: 0.95 }}
            onClick={() => { setPurpose(p); setResult(null); }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-all
              ${purpose === p ? 'bg-primary-600 text-white shadow-md' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}
          >
            {p}
          </motion.button>
        ))}
        <button onClick={() => { setConsent(!consent); setResult(null); }}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
            ${consent ? 'bg-emerald-500 text-white' : 'bg-surface-100 text-surface-600'}`}>
          Consent: {consent ? 'ON' : 'OFF'}
        </button>
        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
          onClick={handlePreview} disabled={loading}
          className="btn-primary ml-auto flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}
              className="w-4 h-4 rounded-full border-2 border-white border-t-transparent" />
          ) : (
            <><Zap className="w-4 h-4" /> Run Masking</>
          )}
        </motion.button>
      </motion.div>

      {error && (
        <motion.div variants={item} className="glass-card-solid p-4 border-l-4 border-red-500 text-red-700 text-sm">
          {error}
        </motion.div>
      )}

      {/* Split View */}
      <motion.div variants={item} className="grid lg:grid-cols-2 gap-4">
        <div className="glass-card-solid p-5">
          <h3 className="text-sm font-semibold text-surface-500 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500"></span> Original Text
          </h3>
          <textarea
            value={inputText}
            onChange={e => { setInputText(e.target.value); setResult(null); }}
            rows={14}
            className="w-full bg-surface-50 rounded-xl p-4 text-sm font-mono text-surface-800
              border border-surface-200 resize-none focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>

        <div className="glass-card-solid p-5">
          <h3 className="text-sm font-semibold text-surface-500 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Masked Output
            {result && (
              <span className="ml-auto badge bg-primary-100 text-primary-600">{result.masking_strategy}</span>
            )}
          </h3>
          {result ? (
            <pre className="bg-surface-50 rounded-xl p-4 text-sm font-mono text-surface-800
              leading-relaxed whitespace-pre-wrap min-h-[280px] border border-surface-200">
              {result.masked_text}
            </pre>
          ) : (
            <div className="bg-surface-50 rounded-xl p-4 min-h-[280px] flex items-center justify-center border border-surface-200">
              <p className="text-surface-400 text-sm flex items-center gap-2">
                Click &quot;Run Masking&quot; to see results <ArrowRight className="w-4 h-4" />
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Entities Detected */}
      {result?.entities?.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-5">
          <h3 className="text-sm font-semibold text-surface-500 mb-3 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-500" />
            {result.entities.length} PII Entities Detected
          </h3>
          <div className="flex flex-wrap gap-2">
            {result.entities.map((e: any, i: number) => (
              <motion.span key={i} initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: i * 0.05 }}
                className={`badge ${entityColors[e.entity_type] || entityColors.DEFAULT}`}
              >
                {e.entity_type}: <span className="font-mono ml-1">{e.text}</span>
                <span className="ml-1 opacity-60">({Math.round(e.score * 100)}%)</span>
              </motion.span>
            ))}
          </div>
          <p className="text-xs text-surface-400 mt-3">Policy: {result.policy_rule}</p>
        </motion.div>
      )}
    </motion.div>
  );
}
