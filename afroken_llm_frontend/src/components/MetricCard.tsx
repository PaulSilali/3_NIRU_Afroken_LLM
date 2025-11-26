import { motion, useReducedMotion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon: LucideIcon;
  iconColor?: string;
  delay?: number;
}

export function MetricCard({
  title,
  value,
  change,
  trend = 'neutral',
  icon: Icon,
  iconColor = 'hsl(var(--primary))',
  delay = 0,
}: MetricCardProps) {
  const trendIcons = {
    up: ArrowUp,
    down: ArrowDown,
    neutral: Minus,
  };

  const trendColors = {
    up: 'text-success',
    down: 'text-destructive',
    neutral: 'text-muted-foreground',
  };

  const TrendIcon = trendIcons[trend];
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
      animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut', delay }}
    >
      <Card className="relative overflow-hidden border-2 shadow-lg transition-shadow duration-300 hover:shadow-glow">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        <CardContent className="p-6 relative">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground mb-2">{title}</p>
              <p className="text-4xl font-display font-bold mb-3">{value}</p>
              {change !== undefined && (
                <div className={`flex items-center gap-1.5 text-sm font-medium ${trendColors[trend]}`}>
                  <TrendIcon className="w-4 h-4" aria-hidden="true" />
                  <span>{Math.abs(change)}%</span>
                  <span className="text-muted-foreground text-xs font-normal">vs last month</span>
                </div>
              )}
            </div>
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center shadow-md group-hover:shadow-glow transition-all duration-300"
              style={{ backgroundColor: iconColor }}
              aria-hidden="true"
            >
              <Icon className="w-7 h-7 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
