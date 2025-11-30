import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { motion, useReducedMotion } from 'framer-motion';
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
  const shouldReduceMotion = useReducedMotion();
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [countyFilter, setCountyFilter] = useState<string>('all');
  
  const { data: metrics, isLoading, error } = useQuery({
    queryKey: ['metrics', countyFilter, timeRange],
    queryFn: () => getMetrics(countyFilter === 'all' ? undefined : countyFilter, timeRange),
    retry: 1,
    staleTime: 0, // Always fresh for smooth filtering
    gcTime: 0, // Don't cache to ensure fresh data on filter change
  });

  // Metrics are already filtered by getMetrics, so use directly
  const filteredTotalQueries = metrics?.totalQueries || 0;
  const filteredEscalations = metrics?.escalations || 0;
  const filteredAvgSatisfaction = metrics?.satisfactionRate || 0;
  const filteredMetrics = metrics;

  const handleExportData = () => {
    if (!metrics) {
      toast.error('No data available to export');
      return;
    }

    try {
      // Create CSV content
      const csvRows: string[] = [];
      
      // Header
      csvRows.push('Dashboard Metrics Export');
      csvRows.push(`Generated: ${new Date().toLocaleString()}`);
      csvRows.push(`Time Range: ${timeRange}`);
      csvRows.push(`County Filter: ${countyFilter === 'all' ? 'All Counties' : countyFilter}`);
      csvRows.push('');
      
      // Summary metrics
      csvRows.push('Summary Metrics');
      csvRows.push('Metric,Value');
      csvRows.push(`Total Queries,${filteredTotalQueries.toLocaleString()}`);
      csvRows.push(`Satisfaction Rate,${filteredAvgSatisfaction}%`);
      csvRows.push(`Average Response Time,${metrics.avgResponseTime}s`);
      csvRows.push(`Escalations,${filteredEscalations.toLocaleString()}`);
      csvRows.push('');
      
      // Top Intents
      csvRows.push('Top Intents');
      csvRows.push('Intent,Count,Percentage');
      metrics.topIntents.forEach(intent => {
        csvRows.push(`${intent.intent},${intent.count},${intent.percentage}%`);
      });
      csvRows.push('');
      
      // County Summary
      csvRows.push('County Summary');
      csvRows.push('County,Queries,Satisfaction %,Escalations');
      (metrics?.countySummary || []).forEach(county => {
        csvRows.push(`${county.countyName},${county.queries},${county.satisfaction},${county.escalations}`);
      });
      
      // Create blob and download
      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `dashboard-export-${timeRange}-${countyFilter === 'all' ? 'all-counties' : countyFilter}-${Date.now()}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success('Data exported successfully!');
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Failed to export data. Please try again.');
    }
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

  if (error) {
    console.error('Dashboard error:', error);
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="space-y-6">
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-destructive mb-2">Error Loading Dashboard</h2>
              <p className="text-muted-foreground">
                {error instanceof Error ? error.message : 'Failed to load dashboard data. Please try again later.'}
              </p>
              <Button 
                onClick={() => window.location.reload()} 
                className="mt-4"
              >
                Reload Page
              </Button>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">
          <div className="space-y-6">
            <div className="bg-muted/10 border border-border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-2">No Data Available</h2>
              <p className="text-muted-foreground">
                Dashboard data is not available. Please try again later.
              </p>
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
              initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
              animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
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

          {/* Filters */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="font-medium">Time range:</span>
                <select
                  className="rounded-md border border-border bg-background px-2 py-1 text-xs focus-ring"
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value as any)}
                >
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="90d">Last 90 days</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-medium">County:</span>
                <select
                  className="rounded-md border border-border bg-background px-2 py-1 text-xs focus-ring"
                  value={countyFilter}
                  onChange={(e) => setCountyFilter(e.target.value)}
                >
                  <option value="all">All counties</option>
                  {metrics?.countySummary.map((c) => (
                    <option key={c.countyName} value={c.countyName}>
                      {c.countyName}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Filters are illustrative in this demo; data represents simulated usage.
            </p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
              title={t('dashboard.metrics.totalQueries')}
              value={filteredTotalQueries.toLocaleString()}
              change={12}
              trend="up"
              icon={MessageSquare}
              iconColor="hsl(var(--primary))"
              delay={0}
            />
            <MetricCard
              title={t('dashboard.metrics.satisfaction')}
              value={`${filteredAvgSatisfaction}%`}
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
              value={filteredEscalations.toLocaleString()}
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
              <CardDescription className="text-base">
                Most common citizen questions and requests ({timeRange === '7d' ? 'last 7 days' : timeRange === '30d' ? 'last 30 days' : 'last 90 days'})
                {countyFilter !== 'all' && ` - ${countyFilter} County`}
              </CardDescription>
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
          <CountyMap 
            filteredCounty={countyFilter === 'all' ? undefined : countyFilter}
            counties={filteredMetrics?.countySummary}
          />

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
