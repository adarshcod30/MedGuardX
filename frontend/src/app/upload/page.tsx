'use client';
import { motion } from 'framer-motion';
import { Upload as UploadIcon, FileText, Image, Activity, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import { Copy, Plus, UserCircle } from 'lucide-react';

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

type Stage = 'idle' | 'detecting' | 'extracting' | 'scanning' | 'encrypting' | 'storing' | 'done' | 'error';

const stageLabels: Record<Stage, string> = {
  idle: 'Waiting for file...',
  detecting: 'Detecting file type...',
  extracting: 'Extracting text content...',
  scanning: 'Scanning for PII entities...',
  encrypting: 'Encrypting data...',
  storing: 'Storing securely...',
  done: 'Upload complete!',
  error: 'Upload failed',
};

export default function UploadPage() {
  const [uploadMode, setUploadMode] = useState<'new' | 'existing'>('new');
  const [existingPatientId, setExistingPatientId] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [stage, setStage] = useState<Stage>('idle');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const processFile = async (file: File) => {
    setResult(null);
    setError('');
    const stages: Stage[] = ['detecting', 'extracting', 'scanning', 'encrypting', 'storing'];
    for (const s of stages) {
      setStage(s);
      await new Promise(r => setTimeout(r, 600));
    }
    try {
      const patientIdParam = uploadMode === 'existing' && existingPatientId.trim() ? existingPatientId.trim() : undefined;
      const res = await api.upload(file, patientIdParam);
      setStage('done');
      setResult(res);
    } catch (e: any) {
      setStage('error');
      setError(e.message || 'Upload failed');
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  const stageIndex = (s: Stage) => ['detecting', 'extracting', 'scanning', 'encrypting', 'storing', 'done'].indexOf(s);

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <h1 className="text-2xl font-bold text-surface-900">Upload Data</h1>
        <p className="text-surface-500 mt-1">Upload HL7, PDF, image, or text files for secure processing</p>
      </motion.div>

      {/* Tabs */}
      <motion.div variants={item} className="flex p-1 bg-surface-100 rounded-xl w-fit">
        <button
          onClick={() => setUploadMode('new')}
          className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
            uploadMode === 'new' ? 'bg-white text-primary-700 shadow-sm' : 'text-surface-500 hover:text-surface-700'
          }`}
        >
          <Plus className="w-4 h-4" /> New Patient
        </button>
        <button
          onClick={() => setUploadMode('existing')}
          className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
            uploadMode === 'existing' ? 'bg-white text-primary-700 shadow-sm' : 'text-surface-500 hover:text-surface-700'
          }`}
        >
          <UserCircle className="w-4 h-4" /> Existing Patient
        </button>
      </motion.div>

      {uploadMode === 'existing' && (
        <motion.div variants={item} initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="glass-card-solid p-6 border border-primary-100">
          <label className="block text-sm font-medium text-surface-700 mb-2">Patient ID</label>
          <input
            type="text"
            className="input w-full"
            placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
            value={existingPatientId}
            onChange={(e) => setExistingPatientId(e.target.value)}
          />
          <p className="text-xs text-surface-400 mt-2">New records will be securely appended to this patient profile.</p>
        </motion.div>
      )}

      {/* Drop Zone */}
      <motion.div
        variants={item}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`glass-card-solid p-12 text-center cursor-pointer transition-all duration-300
          ${dragOver ? 'border-primary-400 bg-primary-50/50 scale-[1.01]' : 'border-surface-200 hover:border-primary-300'}
          border-2 border-dashed`}
      >
        <input type="file" id="fileInput" className="hidden" onChange={handleFileSelect}
          accept=".txt,.hl7,.pdf,.png,.jpg,.jpeg,.tiff,.bmp" />
        <label htmlFor="fileInput" className="cursor-pointer">
          <motion.div
            animate={dragOver ? { scale: 1.1, rotate: 5 } : { scale: 1, rotate: 0 }}
            className="inline-flex p-4 rounded-2xl bg-primary-50 mb-4"
          >
            <UploadIcon className="w-10 h-10 text-primary-500" />
          </motion.div>
          <p className="text-lg font-semibold text-surface-800">
            {dragOver ? 'Drop file here' : 'Drag & drop or click to upload'}
          </p>
          <p className="text-sm text-surface-400 mt-2">Supports HL7, PDF, PNG, JPG, TXT</p>
          <div className="flex justify-center gap-3 mt-4">
            {[
              { icon: '🏥', label: 'HL7' },
              { icon: '📄', label: 'PDF' },
              { icon: '🖼️', label: 'Image' },
              { icon: '📝', label: 'Text' },
            ].map(f => (
              <span key={f.label} className="px-3 py-1.5 rounded-lg bg-surface-100 text-xs font-medium text-surface-600">
                {f.icon} {f.label}
              </span>
            ))}
          </div>
        </label>
      </motion.div>

      {/* Processing Pipeline */}
      {stage !== 'idle' && (
        <motion.div variants={item} initial="hidden" animate="show" className="glass-card-solid p-6">
          <h3 className="font-semibold text-surface-800 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary-500" />
            Processing Pipeline
          </h3>
          <div className="space-y-3">
            {['detecting', 'extracting', 'scanning', 'encrypting', 'storing'].map((s, i) => {
              const current = stageIndex(stage);
              const isComplete = current > i || stage === 'done';
              const isCurrent = stageIndex(stage) === i && stage !== 'done';
              return (
                <motion.div
                  key={s}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-300
                    ${isComplete ? 'bg-emerald-50' : isCurrent ? 'bg-primary-50' : 'bg-surface-50'}`}
                >
                  {isComplete ? (
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                  ) : isCurrent ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}
                      className="w-5 h-5 rounded-full border-2 border-primary-500 border-t-transparent" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-surface-300" />
                  )}
                  <span className={`text-sm font-medium ${isComplete ? 'text-emerald-700' : isCurrent ? 'text-primary-700' : 'text-surface-400'}`}>
                    {stageLabels[s as Stage]}
                  </span>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Result */}
      {stage === 'done' && result && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-6 border-l-4 border-emerald-500">
          <h3 className="font-semibold text-emerald-700 flex items-center gap-2 mb-3">
            <CheckCircle className="w-5 h-5" /> Upload Successful
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-surface-50 rounded-xl p-4 relative group">
              <p className="text-xs text-surface-400">Patient ID</p>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-sm font-mono font-medium text-surface-800 break-all">{result.patient_id}</p>
                <button 
                  onClick={() => {
                    navigator.clipboard.writeText(result.patient_id);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="p-1.5 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors shrink-0"
                  title="Copy Patient ID"
                >
                  {copied ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="bg-surface-50 rounded-xl p-4">
              <p className="text-xs text-surface-400">File Type</p>
              <p className="text-sm font-medium text-surface-800 mt-1 uppercase">{result.file_type}</p>
            </div>
            <div className="bg-surface-50 rounded-xl p-4">
              <p className="text-xs text-surface-400">PII Entities Found</p>
              <p className="text-sm font-medium text-surface-800 mt-1">{result.entities_detected?.length || 0} entities</p>
            </div>
          </div>
          {result.entities_detected?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-surface-400 mb-2">Detected Entities</p>
              <div className="flex flex-wrap gap-2">
                {result.entities_detected.map((e: any, i: number) => (
                  <span key={i} className="badge bg-rose-100 text-rose-700">
                    {e.entity_type}: {e.text}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {stage === 'error' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card-solid p-6 border-l-4 border-red-500">
          <p className="text-red-700 font-medium flex items-center gap-2">
            <XCircle className="w-5 h-5" /> {error}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}
