'use client';

import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';

interface DeleteAccountDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  userName: string;
}

export default function DeleteAccountDialog({
  isOpen,
  onClose,
  onConfirm,
  userName,
}: DeleteAccountDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  if (!isOpen) return null;

  const handleConfirm = async () => {
    if (confirmText !== 'DELETE') return;

    setIsDeleting(true);
    try {
      await onConfirm();
    } catch (error) {
      console.error('Error deleting account:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const isConfirmValid = confirmText === 'DELETE';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-card border border-border rounded-theme shadow-xl max-w-md w-full p-6 relative">
        {/* Close button */}
        <button
          onClick={onClose}
          disabled={isDeleting}
          className="absolute top-4 right-4 text-muted-foreground hover:text-card-foreground transition-colors disabled:opacity-50"
          aria-label="Close dialog"
        >
          <X size={20} />
        </button>

        {/* Warning Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 rounded-full bg-error/10 flex items-center justify-center">
            <AlertTriangle size={32} className="text-error" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-card-foreground text-center mb-2">
          Delete Account
        </h2>

        {/* Warning Message */}
        <div className="bg-error/10 border border-error/30 rounded-theme p-4 mb-4">
          <p className="text-sm text-card-foreground font-medium mb-2">
            ⚠️ This action cannot be undone!
          </p>
          <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
            <li>Your account will be permanently deleted</li>
            <li>All your activity logs will be removed</li>
            <li>Your earnings data will be lost</li>
            <li>You will be removed from your family group</li>
          </ul>
        </div>

        {/* Confirmation Input */}
        <div className="mb-6">
          <label htmlFor="confirm-delete" className="block text-sm font-medium text-card-foreground mb-2">
            Type <span className="font-mono font-bold">DELETE</span> to confirm:
          </label>
          <input
            id="confirm-delete"
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            disabled={isDeleting}
            className="w-full px-4 py-2 border border-border rounded-theme bg-background text-card-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
            placeholder="Type DELETE"
            autoComplete="off"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            disabled={isDeleting}
            className="flex-1 px-4 py-2 border border-border rounded-theme text-card-foreground hover:bg-muted transition-colors duration-200 disabled:opacity-50 min-h-touch"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!isConfirmValid || isDeleting}
            className="flex-1 px-4 py-2 bg-error text-white font-medium rounded-theme hover:bg-error/90 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-touch"
          >
            {isDeleting ? 'Deleting...' : 'Delete Account'}
          </button>
        </div>
      </div>
    </div>
  );
}
