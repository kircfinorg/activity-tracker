'use client';

export function SkeletonCard() {
  return (
    <div className="bg-card border border-border rounded-theme p-4 shadow-sm animate-pulse">
      <div className="h-4 bg-muted rounded w-3/4 mb-3"></div>
      <div className="h-3 bg-muted rounded w-1/2 mb-2"></div>
      <div className="h-3 bg-muted rounded w-2/3"></div>
    </div>
  );
}

export function SkeletonActivityCard() {
  return (
    <div className="bg-card border border-border rounded-theme p-6 shadow-sm animate-pulse">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="h-5 bg-muted rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
        </div>
        <div className="h-10 w-10 bg-muted rounded-full"></div>
      </div>
      <div className="h-3 bg-muted rounded w-1/3"></div>
    </div>
  );
}

export function SkeletonActivityGrid() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <SkeletonActivityCard />
      <SkeletonActivityCard />
      <SkeletonActivityCard />
      <SkeletonActivityCard />
      <SkeletonActivityCard />
      <SkeletonActivityCard />
    </div>
  );
}

export function SkeletonVerificationItem() {
  return (
    <div className="bg-card border border-border rounded-theme p-4 shadow-sm animate-pulse">
      <div className="flex items-center gap-3 mb-3">
        <div className="h-10 w-10 bg-muted rounded-full"></div>
        <div className="flex-1">
          <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-muted rounded w-1/3"></div>
        </div>
      </div>
      <div className="flex gap-2">
        <div className="h-9 bg-muted rounded flex-1"></div>
        <div className="h-9 bg-muted rounded flex-1"></div>
      </div>
    </div>
  );
}

export function SkeletonVerificationQueue() {
  return (
    <div className="space-y-3">
      <SkeletonVerificationItem />
      <SkeletonVerificationItem />
      <SkeletonVerificationItem />
    </div>
  );
}

export function SkeletonEarningsCard() {
  return (
    <div className="bg-card border border-border rounded-theme p-6 shadow-sm animate-pulse">
      <div className="h-4 bg-muted rounded w-1/2 mb-3"></div>
      <div className="h-8 bg-muted rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-muted rounded w-1/3"></div>
    </div>
  );
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
