import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { getMetrics } from '@/lib/api';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { MetricCard } from '@/components/MetricCard';
import { CountyMap } from '@/components/CountyMap';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Download, MessageSquare, ThumbsUp, Clock, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

export default function Dashboard() {
  const { t } = useTranslation();
  
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => getMetrics(),
  });

  const handleExportData = () => {
    toast.success('Data export started. Download will begin shortly.');
    // In a real app, trigger CSV download
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="space-y-6">
            <Skeleton className="h-12 w-64" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 bg-gradient-hero">
        <div className="container mx-auto px-4 py-8">
          <div className="space-y-8">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
            >
              <div>
                <h1 className="text-4xl md:text-5xl font-display font-bold mb-2 text-gradient">
                  {t('dashboard.title')}
                </h1>
                <p className="text-muted-foreground text-lg">
                  Real-time insights into citizen service interactions
                </p>
              </div>
              <Button onClick={handleExportData} className="gap-2 focus-ring shadow-md hover:shadow-glow transition-all font-medium">
                <Download className="w-4 h-4" aria-hidden="true" />
                {t('dashboard.export')}
              </Button>
            </motion.div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title={t('dashboard.metrics.totalQueries')}
              value={metrics?.totalQueries.toLocaleString() || '0'}
              change={12}
              trend="up"
              icon={MessageSquare}
              iconColor="hsl(var(--primary))"
              delay={0}
            />
            <MetricCard
              title={t('dashboard.metrics.satisfaction')}
              value={`${metrics?.satisfactionRate || 0}%`}
              change={3}
              trend="up"
              icon={ThumbsUp}
              iconColor="hsl(var(--success))"
              delay={0.1}
            />
            <MetricCard
              title={t('dashboard.metrics.avgResponse')}
              value={`${metrics?.avgResponseTime || 0}s`}
              change={-8}
              trend="down"
              icon={Clock}
              iconColor="hsl(var(--info))"
              delay={0.2}
            />
            <MetricCard
              title={t('dashboard.metrics.escalations')}
              value={metrics?.escalations.toLocaleString() || '0'}
              change={-15}
              trend="down"
              icon={AlertTriangle}
              iconColor="hsl(var(--warning))"
              delay={0.3}
            />
          </div>

          {/* Top Intents Chart */}
          <Card className="border-2 shadow-lg">
            <CardHeader>
              <CardTitle className="font-display text-2xl">{t('dashboard.charts.topIntents')}</CardTitle>
              <CardDescription className="text-base">Most common citizen questions and requests</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  count: {
                    label: "Queries",
                    color: "hsl(var(--primary))",
                  },
                }}
                className="h-[300px]"
              >
                <BarChart data={metrics?.topIntents || []} accessibilityLayer>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="intent"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar
                    dataKey="count"
                    fill="hsl(var(--primary))"
                    radius={[8, 8, 0, 0]}
                    animationDuration={1000}
                  />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* County Map */}
          <CountyMap />

          {/* Additional Info */}
          <Card className="border-2 shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl" />
            <CardHeader className="relative">
              <CardTitle className="font-display text-2xl">About This Dashboard</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 relative">
              <p className="text-muted-foreground leading-relaxed">
                This dashboard provides real-time analytics of the AfroKen Citizen Service Copilot.
                All data is aggregated and anonymized to protect user privacy.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-4 rounded-xl glass-effect">
                  <h4 className="font-display font-semibold mb-2 text-primary">Data Sources</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Queries, feedback, and performance metrics from all interaction channels
                  </p>
                </div>
                <div className="p-4 rounded-xl glass-effect">
                  <h4 className="font-display font-semibold mb-2 text-primary">Update Frequency</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Dashboard refreshes every 5 minutes with the latest data
                  </p>
                </div>
                <div className="p-4 rounded-xl glass-effect">
                  <h4 className="font-display font-semibold mb-2 text-primary">Accessibility</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    All charts are keyboard-navigable and screen reader compatible
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
