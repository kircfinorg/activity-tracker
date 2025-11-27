'use client';

import { useState, useEffect } from 'react';
import { Activity } from '@/types';
import { getIdToken } from '@/lib/auth';

interface FamilyMember {
  uid: string;
  displayName: string;
  role: 'parent' | 'child';
}

interface CreateActivityFormProps {
  familyId: string;
  onActivityCreated: (activity: Activity) => void;
  onCancel?: () => void;
}

export default function CreateActivityForm({
  familyId,
  onActivityCreated,
  onCancel,
}: CreateActivityFormProps) {
  const [name, setName] = useState('');
  const [unit, setUnit] = useState('');
  const [rate, setRate] = useState('');
  const [children, setChildren] = useState<FamilyMember[]>([]);
  const [selectedChildren, setSelectedChildren] = useState<string[]>([]);
  const [assignToAll, setAssignToAll] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingChildren, setIsLoadingChildren] = useState(true);
  const [errors, setErrors] = useState<{
    name?: string;
    unit?: string;
    rate?: string;
    assignment?: string;
    general?: string;
  }>({});

  // Fetch family children on mount
  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const token = await getIdToken();
        if (!token) return;

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/families/${familyId}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          const childMembers = data.members.filter((m: any) => m.role === 'child');
          setChildren(childMembers.map((m: any) => ({
            uid: m.uid,
            displayName: m.display_name || m.displayName || 'Child',
            role: m.role
          })));
        }
      } catch (error) {
        console.error('Error fetching children:', error);
      } finally {
        setIsLoadingChildren(false);
      }
    };

    fetchChildren();
  }, [familyId]);

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    // Validate name (Requirement 5.2)
    if (!name.trim()) {
      newErrors.name = 'Activity name is required';
    }

    // Validate unit (Requirement 5.3)
    if (!unit.trim()) {
      newErrors.unit = 'Unit is required';
    }

    // Validate rate (Requirement 5.4)
    const rateNum = parseFloat(rate);
    if (!rate || isNaN(rateNum)) {
      newErrors.rate = 'Rate is required';
    } else if (rateNum <= 0) {
      newErrors.rate = 'Rate must be a positive value';
    }

    // Validate assignment
    if (!assignToAll && selectedChildren.length === 0 && children.length > 0) {
      newErrors.assignment = 'Please select at least one child or assign to all';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const toggleChildSelection = (childId: string) => {
    setSelectedChildren(prev =>
      prev.includes(childId)
        ? prev.filter(id => id !== childId)
        : [...prev, childId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const token = await getIdToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Determine assigned_to value
      const assignedTo = assignToAll ? null : selectedChildren;

      // Call API to create activity
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/activities`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            family_id: familyId,
            name: name.trim(),
            unit: unit.trim(),
            rate: parseFloat(rate),
            assigned_to: assignedTo,
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to create activity' }));
        throw new Error(error.detail || 'Failed to create activity');
      }

      const data = await response.json();
      
      // Convert createdAt string to Date
      const activity: Activity = {
        ...data.activity,
        createdAt: new Date(data.activity.created_at),
        assignedTo: data.activity.assigned_to,
      };

      // Reset form
      setName('');
      setUnit('');
      setRate('');
      setSelectedChildren([]);
      setAssignToAll(true);

      // Notify parent component
      onActivityCreated(activity);
    } catch (error: any) {
      console.error('Error creating activity:', error);
      setErrors({
        general: error.message || 'Failed to create activity. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Responsive form layout (Requirement 13.1, 13.2)
  return (
    <form onSubmit={handleSubmit} className="space-y-4 animate-fade-in">
      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-1 text-card-foreground">
          Activity Name *
        </label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
          className={`w-full min-h-touch px-3 py-3 text-sm sm:text-base border rounded-theme bg-background text-card-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all ${
            errors.name ? 'border-error' : 'border-border focus:border-primary'
          }`}
          placeholder="e.g., Reading, Exercise, Homework"
          disabled={isSubmitting}
        />
        {errors.name && (
          <p className="mt-1 text-xs sm:text-sm text-error animate-slide-in-down">{errors.name}</p>
        )}
      </div>

      <div>
        <label htmlFor="unit" className="block text-sm font-medium mb-1 text-card-foreground">
          Unit *
        </label>
        <input
          type="text"
          id="unit"
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          className={`w-full min-h-touch px-3 py-3 text-sm sm:text-base border rounded-theme bg-background text-card-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all ${
            errors.unit ? 'border-error' : 'border-border focus:border-primary'
          }`}
          placeholder="e.g., Pages, Minutes, Problems"
          disabled={isSubmitting}
        />
        {errors.unit && (
          <p className="mt-1 text-xs sm:text-sm text-error animate-slide-in-down">{errors.unit}</p>
        )}
      </div>

      <div>
        <label htmlFor="rate" className="block text-sm font-medium mb-1 text-card-foreground">
          Rate ($ per unit) *
        </label>
        <input
          type="number"
          id="rate"
          value={rate}
          onChange={(e) => setRate(e.target.value)}
          step="0.01"
          min="0.01"
          className={`w-full min-h-touch px-3 py-3 text-sm sm:text-base border rounded-theme bg-background text-card-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all ${
            errors.rate ? 'border-error' : 'border-border focus:border-primary'
          }`}
          placeholder="e.g., 0.10"
          disabled={isSubmitting}
        />
        {errors.rate && (
          <p className="mt-1 text-xs sm:text-sm text-error animate-slide-in-down">{errors.rate}</p>
        )}
      </div>

      {/* Child Assignment Section */}
      {!isLoadingChildren && children.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2 text-card-foreground">
            Assign To
          </label>
          
          <div className="space-y-2">
            {/* Assign to All Option */}
            <label className="flex items-center p-3 border border-border rounded-theme hover:bg-muted cursor-pointer transition-colors">
              <input
                type="checkbox"
                checked={assignToAll}
                onChange={(e) => {
                  setAssignToAll(e.target.checked);
                  if (e.target.checked) {
                    setSelectedChildren([]);
                  }
                }}
                disabled={isSubmitting}
                className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
              />
              <span className="ml-3 text-sm text-card-foreground font-medium">
                All Children
              </span>
            </label>

            {/* Individual Children */}
            {!assignToAll && (
              <div className="pl-4 space-y-2 border-l-2 border-border">
                {children.map((child) => (
                  <label
                    key={child.uid}
                    className="flex items-center p-2 hover:bg-muted rounded-theme cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={selectedChildren.includes(child.uid)}
                      onChange={() => toggleChildSelection(child.uid)}
                      disabled={isSubmitting}
                      className="w-4 h-4 text-primary border-border rounded focus:ring-2 focus:ring-primary"
                    />
                    <span className="ml-3 text-sm text-card-foreground">
                      {child.displayName}
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {errors.assignment && (
            <p className="mt-1 text-xs sm:text-sm text-error animate-slide-in-down">{errors.assignment}</p>
          )}
        </div>
      )}

      {errors.general && (
        <div className="p-3 bg-error/10 border border-error/30 rounded-theme animate-slide-in-down">
          <p className="text-xs sm:text-sm text-error">{errors.general}</p>
        </div>
      )}

      {/* Touch-friendly buttons (Requirement 13.2) */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 min-h-touch px-4 py-3 bg-primary text-white rounded-theme hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base font-medium transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          {isSubmitting ? 'Creating...' : 'Create Activity'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="min-h-touch px-4 py-3 border border-border rounded-theme hover:bg-muted focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base font-medium text-card-foreground transition-all"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
