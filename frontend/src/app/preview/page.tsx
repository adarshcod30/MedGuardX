'use client';
import { motion } from 'framer-motion';
import { Eye, Zap, ShieldAlert, ArrowRight } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/lib/api';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const entityColors: Record<string, string> = {
  PERSON: 'bg-blue-100 text-blue-700',
  PHONE_NUMBER: 'bg-amber-100 text-amber-700',
  EMAIL_ADDRESS: 'bg-teal-100 text-teal-700',
  LOCATION: 'bg-purple-100 text-purple-700',
  DATE_TIME: 'bg-pink-100 text-pink-700',
  CREDIT_CARD: 'bg-red-100 text-red-700',
  IN_AADHAAR: 'bg-orange-100 text-orange-700',
  IN_PAN: 'bg-indigo-100 text-indigo-700',
  DEFAULT: 'bg-gray-100 text-gray-700',
};

const sampleTexts = [
  {
    label: '🏥 Patient Record',
    text: `Patient Name: Dr. Rajesh Kumar Sharma
Phone: +91-9876543210
Email: rajesh.sharma@hospital.org
Aadhaar: 4532-8876-1234
DOB: 15-March-1985
Address: 42, MG Road, Bangalore, Karnataka 560001
Diagnosis: Type-2 Diabetes Mellitus with hypertension
Prescription: Metformin 500mg, Amlodipine 5mg
Insurance ID: STAR-HEALTH-2024-889922`,
  },
  {
    label: '📋 Discharge Summary',
    text: `Patient: Priya Patel (Female, 34 years)
MRN: MH-2024-55891
Contact: priya.patel@gmail.com | 8899776655
PAN: ABCDE1234F
Admitted: 12-Jan-2024 | Discharged: 18-Jan-2024
Treating Doctor: Dr. Ananya Mehta
Hospital: Apollo Hospitals, Chennai
Diagnosis: Acute appendicitis — Laparoscopic appendectomy performed
Follow-up: 25-Jan-2024 at OPD, Building B`,
  },
];

export default function PreviewPage() {
  const [inputText, setInputText] = useState(sampleTexts[0].text);
  const [role, setRole] = useState('researcher');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handlePreview = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    try {
      const res = await api.preview(inputText, role, 'research', false);
      setResult(res);
    } catch {
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <h1 className="text-2xl font-bold text-surface-900 flex items-center gap-2">
          <Eye className="w-6 h-6 text-primary-500" /> Mask Preview
        </h1>
        <p className="text-surface-500 mt-1">Paste or select sample text to see live PII masking</p>
      </motion.div>

      {/* Sample Selector */}
      <motion.div variants={item} className="flex gap-3">
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

      {/* Role + Button */}
      <motion.div variants={item} className="flex items-center gap-3 flex-wrap">
        <span className="text-sm font-medium text-surface-600">View as:</span>
        {['doctor', 'nurse', 'researcher', 'company'].map(r => (
          <motion.button key={r} whileTap={{ scale: 0.95 }}
            onClick={() => { setRole(r); setResult(null); }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-all
              ${role === r ? 'bg-primary-600 text-white shadow-md' : 'bg-surface-100 text-surface-600 hover:bg-surface-200'}`}
          >
            {r}
          </motion.button>
        ))}
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

      {/* Split View */}
      <motion.div variants={item} className="grid lg:grid-cols-2 gap-4">
        {/* Input */}
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

        {/* Output */}
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
