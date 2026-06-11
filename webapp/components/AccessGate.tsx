"use client";

import { useRef } from "react";

/**
 * Minimal invite-code gate. Shown after a request comes back 401;
 * stores the code and retries the interrupted send.
 */
export function AccessGate({ onSubmit }: { onSubmit: (code: string) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);

  const submit = () => {
    const code = inputRef.current?.value.trim();
    if (code) onSubmit(code);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-80 rounded-lg border border-gray-700 bg-gray-900 p-6 space-y-4">
        <h2 className="text-sm font-semibold text-gray-200">Access code</h2>
        <p className="text-xs text-gray-500 leading-relaxed">
          This is a private research preview. Enter the invite code you were
          given to continue.
        </p>
        <input
          ref={inputRef}
          type="password"
          autoFocus
          onKeyDown={(e) => e.key === "Enter" && submit()}
          className="w-full rounded bg-gray-800 border border-gray-700 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          onClick={submit}
          className="w-full rounded bg-indigo-600 hover:bg-indigo-500 px-3 py-2 text-sm font-medium text-white transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
