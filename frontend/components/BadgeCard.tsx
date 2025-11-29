'use client';

interface BadgeCardProps {
  badge: {
    id: string;
    name: string;
    description: string;
    icon: string;
    rarity: string;
    earned: boolean;
    earnedAt?: string | null;
  };
}

const rarityColors = {
  common: 'bg-gray-100 border-gray-300 text-gray-700',
  rare: 'bg-blue-100 border-blue-300 text-blue-700',
  epic: 'bg-purple-100 border-purple-300 text-purple-700',
  legendary: 'bg-yellow-100 border-yellow-300 text-yellow-700',
};

const rarityGlow = {
  common: '',
  rare: 'shadow-blue-200',
  epic: 'shadow-purple-200',
  legendary: 'shadow-yellow-200 animate-pulse',
};

export default function BadgeCard({ badge }: BadgeCardProps) {
  const colorClass = rarityColors[badge.rarity as keyof typeof rarityColors] || rarityColors.common;
  const glowClass = badge.earned ? rarityGlow[badge.rarity as keyof typeof rarityGlow] : '';
  
  return (
    <div
      className={`relative p-4 rounded-theme border-2 transition-all ${
        badge.earned
          ? `${colorClass} ${glowClass} shadow-md`
          : 'bg-muted border-border opacity-50 grayscale'
      }`}
    >
      {/* Badge Icon */}
      <div className="text-center mb-2">
        <span className="text-4xl">{badge.icon}</span>
      </div>
      
      {/* Badge Name */}
      <h3 className="text-sm font-bold text-center mb-1 text-card-foreground">
        {badge.name}
      </h3>
      
      {/* Badge Description */}
      <p className="text-xs text-center text-muted-foreground mb-2">
        {badge.description}
      </p>
      
      {/* Rarity Badge */}
      <div className="flex justify-center">
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${colorClass}`}>
          {badge.rarity.charAt(0).toUpperCase() + badge.rarity.slice(1)}
        </span>
      </div>
      
      {/* Earned Date */}
      {badge.earned && badge.earnedAt && (
        <p className="text-xs text-center text-muted-foreground mt-2">
          Earned {new Date(badge.earnedAt).toLocaleDateString()}
        </p>
      )}
      
      {/* Locked Overlay */}
      {!badge.earned && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 rounded-theme">
          <span className="text-3xl">🔒</span>
        </div>
      )}
    </div>
  );
}
