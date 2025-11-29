'use client';

import { useEffect, useState } from 'react';
import { getIdToken } from '@/lib/auth';
import BadgeCard from './BadgeCard';
import { Trophy } from 'lucide-react';

interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  rarity: string;
  earned: boolean;
  earnedAt?: string | null;
}

interface BadgeCollectionProps {
  userId: string;
}

export default function BadgeCollection({ userId }: BadgeCollectionProps) {
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [totalEarned, setTotalEarned] = useState(0);
  const [totalAvailable, setTotalAvailable] = useState(0);

  useEffect(() => {
    fetchBadges();
  }, [userId]);

  const fetchBadges = async () => {
    try {
      const token = await getIdToken();
      if (!token) return;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/badges/user/${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch badges');
      }

      const data = await response.json();
      const badgesArray = Object.values(data.badges) as Badge[];
      setBadges(badgesArray);
      setTotalEarned(data.total_earned);
      setTotalAvailable(data.total_available);
    } catch (err: any) {
      console.error('Error fetching badges:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredBadges = badges.filter(badge => {
    if (filter === 'all') return true;
    if (filter === 'earned') return badge.earned;
    if (filter === 'locked') return !badge.earned;
    return badge.category === filter;
  });

  const categories = ['all', 'earned', 'locked', 'activity', 'earnings', 'streak', 'reading', 'special'];

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="w-12 h-12 border-4 border-gray-300 border-t-primary rounded-full animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Loading badges...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-error">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Trophy className="text-primary" size={32} />
          <div>
            <h2 className="text-2xl font-bold text-card-foreground">Badge Collection</h2>
            <p className="text-sm text-muted-foreground">
              {totalEarned} of {totalAvailable} earned
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-primary">{totalEarned}</div>
          <div className="text-xs text-muted-foreground">Badges</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-muted rounded-full h-3">
        <div
          className="bg-primary h-3 rounded-full transition-all duration-500"
          style={{ width: `${(totalEarned / totalAvailable) * 100}%` }}
        />
      </div>

      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-4 py-2 rounded-theme text-sm font-medium transition-colors ${
              filter === cat
                ? 'bg-primary text-white'
                : 'bg-muted text-card-foreground hover:bg-primary/20'
            }`}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {/* Badge Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {filteredBadges.map((badge) => (
          <BadgeCard key={badge.id} badge={badge} />
        ))}
      </div>

      {filteredBadges.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No badges in this category yet</p>
        </div>
      )}
    </div>
  );
}
