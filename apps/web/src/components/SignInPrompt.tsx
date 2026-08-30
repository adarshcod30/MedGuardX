'use client';
import Link from 'next/link';
import { Lock, LogIn } from 'lucide-react';

/** Shown on protected pages when there is no active session. */
export default function SignInPrompt({ action = 'use this feature' }: { action?: string }) {
  return (
    <div className="glass-card-solid p-12 text-center max-w-md mx-auto mt-8">
      <div className="inline-flex p-3 rounded-2xl bg-surface-100 mb-4">
        <Lock className="w-8 h-8 text-surface-400" />
      </div>
      <h2 className="text-lg font-semibold text-surface-800">Sign in required</h2>
      <p className="text-surface-500 text-sm mt-1 mb-5">
        You need to be signed in to {action}. Your role determines what data you can see.
      </p>
      <Link href="/login" className="btn-primary inline-flex items-center gap-2">
        <LogIn className="w-4 h-4" /> Go to Sign In
      </Link>
    </div>
  );
}
