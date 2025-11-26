import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ServiceType } from '@/types';
import * as Icons from 'lucide-react';

interface ServiceCardProps {
  service: {
    id: ServiceType;
    name: string;
    icon: string;
    color: string;
  };
  onClick: () => void;
}

export function ServiceCard({ service, onClick }: ServiceCardProps) {
  const { t } = useTranslation();
  const Icon = Icons[service.icon as keyof typeof Icons] as LucideIcon;

  return (
    <Card
      className="smooth-transition hover-lift cursor-pointer focus-ring h-full border-2 hover:border-primary/50 group relative overflow-hidden bg-gradient-to-br from-card via-card to-primary/5"
      onClick={onClick}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      role="button"
      aria-label={`${service.name}: ${t(`home.services.${service.id}.description`)}`}
    >
      {/* Animated gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
      <div className="absolute -top-16 -right-16 w-48 h-48 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700" />
      
      <CardHeader className="relative p-8">
        <div
          className="w-20 h-20 rounded-3xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-glow group-hover:scale-110 group-hover:rotate-3 transition-all duration-500"
          style={{ background: `linear-gradient(135deg, ${service.color}, ${service.color}dd)` }}
          aria-hidden="true"
        >
          {Icon && <Icon className="w-10 h-10 text-white" />}
        </div>
        <CardTitle className="text-2xl font-display mb-3 group-hover:text-primary transition-colors font-bold">
          {t(`home.services.${service.id}.title`)}
        </CardTitle>
        <CardDescription className="text-base leading-relaxed">
          {t(`home.services.${service.id}.description`)}
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
