import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Upload,
  Globe,
  FileText,
  Settings,
  LogOut,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Download,
  Trash2,
  Eye,
  AlertCircle,
  Database,
  Cpu,
  Volume2,
  Mic,
  Sparkles,
  BarChart3,
  FileCheck,
  Link as LinkIcon,
  Users,
  MessageSquare,
  Globe2,
  Phone,
  Smartphone,
  Shield,
  Lock,
  TrendingUp,
  Activity,
  MapPin,
  Languages,
  Zap,
  Server,
  FileSearch,
  BookOpen,
  AlertTriangle,
  CheckCircle,
  X,
  PlayCircle,
  PauseCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { Header } from '@/components/Header';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API Functions
async function uploadPDF(file: File, category?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (category) formData.append('category', category);

  const response = await fetch(`${API_BASE_URL}/api/v1/admin/documents/upload-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    // Try to extract error message from response
    let errorMessage = 'Upload failed';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

async function scrapeURL(url: string, category?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/documents/scrape-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, category }),
  });

  if (!response.ok) {
    // Try to extract error message from response
    let errorMessage = 'Scraping failed';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

async function getJobs(status?: string, jobType?: string) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (jobType) params.append('job_type', jobType);

  const response = await fetch(`${API_BASE_URL}/api/v1/admin/jobs?${params}`);
  if (!response.ok) throw new Error('Failed to fetch jobs');
  return response.json();
}

async function getJobStatus(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/jobs/${jobId}`);
  if (!response.ok) throw new Error('Failed to fetch job status');
  return response.json();
}

async function deleteJob(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/jobs/${jobId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete job');
  }
  return response.json();
}

async function deleteJobs(jobIds: string[]) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/jobs`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(jobIds),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete jobs');
  }
  return response.json();
}

async function createService(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/services`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create service');
  }
  return response.json();
}

async function createHudumaCentre(data: {
  name: string;
  county: string;
  sub_county?: string;
  town?: string;
  latitude?: number;
  longitude?: number;
  contact_phone?: string;
  contact_email?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/huduma-centres`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create Huduma Centre');
  }
  return response.json();
}

// Mock data for demonstration
const countyData = [
  { name: 'Nairobi', queries: 12500, satisfaction: 87, escalations: 45 },
  { name: 'Mombasa', queries: 8900, satisfaction: 82, escalations: 32 },
  { name: 'Kisumu', queries: 6700, satisfaction: 85, escalations: 28 },
  { name: 'Nakuru', queries: 5400, satisfaction: 80, escalations: 22 },
];

const channelData = [
  { name: 'WhatsApp', value: 45, color: '#25D366' },
  { name: 'Web', value: 30, color: '#006A4E' },
  { name: 'USSD', value: 15, color: '#FF6B35' },
  { name: 'SMS', value: 7, color: '#4A90E2' },
  { name: 'Voice', value: 3, color: '#9B59B6' },
];

const serviceData = [
  { service: 'NHIF', queries: 3420, completion: 89 },
  { service: 'KRA', queries: 2890, completion: 92 },
  { service: 'NSSF', queries: 1560, completion: 85 },
  { service: 'Huduma', queries: 2340, completion: 88 },
  { service: 'NTSA', queries: 1890, completion: 90 },
];

const languageData = [
  { language: 'Swahili', percentage: 65, queries: 12500 },
  { language: 'English', percentage: 25, queries: 4800 },
  { language: 'Sheng', percentage: 10, queries: 1920 },
];

export default function AdminDashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [selectedTab, setSelectedTab] = useState('overview');
  const [pdfCategory, setPdfCategory] = useState('');
  const [urlToScrape, setUrlToScrape] = useState('');
  const [urlCategory, setUrlCategory] = useState('');
  const [selectedJob, setSelectedJob] = useState<string | null>(null);
  const [selectedCounty, setSelectedCounty] = useState('all');
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [serviceFormOpen, setServiceFormOpen] = useState(false);
  const [hudumaFormOpen, setHudumaFormOpen] = useState(false);
  const [newService, setNewService] = useState({ title: '', description: '', category: 'general', logo: null as File | null });
  const [newHuduma, setNewHuduma] = useState({ 
    name: '', county: '', sub_county: '', town: '', 
    latitude: '', longitude: '', contact_phone: '', contact_email: '' 
  });
  const [modelSettings, setModelSettings] = useState({
    llmEndpoint: '',
    fineTunedEndpoint: '',
    embeddingEndpoint: '',
    usePostgreSQL: true,
    useMinIO: true,
    whisperEnabled: true,
    ttsEnabled: true,
  });

  // Check authentication
  const authToken = localStorage.getItem('authToken');
  if (!authToken) {
    navigate('/login');
    return null;
  }

  // Queries
  const { data: jobsData, isLoading: jobsLoading } = useQuery({
    queryKey: ['admin-jobs'],
    queryFn: () => getJobs(),
    refetchInterval: 5000,
  });

  const { data: jobStatus } = useQuery({
    queryKey: ['job-status', selectedJob],
    queryFn: () => getJobStatus(selectedJob!),
    enabled: !!selectedJob,
    refetchInterval: 2000,
  });

  // Mutations
  const uploadMutation = useMutation({
    mutationFn: ({ file, category }: { file: File; category?: string }) =>
      uploadPDF(file, category),
    onSuccess: (data) => {
      toast.success('PDF upload started! Check processing status.');
      queryClient.invalidateQueries({ queryKey: ['admin-jobs'] });
      // Reset form: clear file input and category
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setPdfCategory(''); // Reset category dropdown
    },
    onError: (error: Error) => {
      // Display the error message (which now includes backend instructions)
      const message = error.message || 'Upload failed';
      toast.error(message, { duration: 10000 }); // Show for 10 seconds so user can read it
    },
  });

  const scrapeMutation = useMutation({
    mutationFn: ({ url, category }: { url: string; category?: string }) =>
      scrapeURL(url, category),
    onSuccess: (data) => {
      toast.success('URL scraping started! Check processing status.');
      setUrlToScrape('');
      queryClient.invalidateQueries({ queryKey: ['admin-jobs'] });
    },
    onError: (error: Error) => {
      // Display the error message (which now includes backend instructions)
      const message = error.message || 'Scraping failed';
      toast.error(message, { duration: 10000 }); // Show for 10 seconds so user can read it
    },
  });

  const serviceMutation = useMutation({
    mutationFn: async () => {
      const formData = new FormData();
      formData.append('title', newService.title);
      formData.append('description', newService.description);
      formData.append('category', newService.category);
      if (newService.logo) {
        formData.append('logo', newService.logo);
      }
      return createService(formData);
    },
    onSuccess: () => {
      toast.success('Service created successfully!');
      setNewService({ title: '', description: '', category: 'general', logo: null });
      setServiceFormOpen(false);
      queryClient.invalidateQueries({ queryKey: ['services'] });
    },
    onError: (error: any) => {
      toast.error(`Failed to create service: ${error.message}`);
    },
  });

  const hudumaMutation = useMutation({
    mutationFn: () => createHudumaCentre({
      name: newHuduma.name,
      county: newHuduma.county,
      sub_county: newHuduma.sub_county || undefined,
      town: newHuduma.town || undefined,
      latitude: newHuduma.latitude ? parseFloat(newHuduma.latitude) : undefined,
      longitude: newHuduma.longitude ? parseFloat(newHuduma.longitude) : undefined,
      contact_phone: newHuduma.contact_phone || undefined,
      contact_email: newHuduma.contact_email || undefined,
    }),
    onSuccess: () => {
      toast.success('Huduma Centre created successfully!');
      setNewHuduma({ name: '', county: '', sub_county: '', town: '', latitude: '', longitude: '', contact_phone: '', contact_email: '' });
      setHudumaFormOpen(false);
    },
    onError: (error: any) => {
      toast.error(`Failed to create Huduma Centre: ${error.message}`);
    },
  });

  const deleteJobsMutation = useMutation({
    mutationFn: (jobIds: string[]) => deleteJobs(jobIds),
    onSuccess: (data) => {
      toast.success(`Deleted ${data.deleted_count} job(s) successfully!`);
      setSelectedJobs(new Set());
      queryClient.invalidateQueries({ queryKey: ['admin-jobs'] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete jobs: ${error.message}`);
    },
  });

  const handleSelectJob = (jobId: string) => {
    const newSelected = new Set(selectedJobs);
    if (newSelected.has(jobId)) {
      newSelected.delete(jobId);
    } else {
      newSelected.add(jobId);
    }
    setSelectedJobs(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedJobs.size === jobsData?.jobs?.length) {
      setSelectedJobs(new Set());
    } else {
      setSelectedJobs(new Set(jobsData?.jobs?.map((j: any) => j.job_id) || []));
    }
  };

  const handleDeleteSelected = () => {
    if (selectedJobs.size === 0) return;
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    deleteJobsMutation.mutate(Array.from(selectedJobs));
    setDeleteDialogOpen(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    navigate('/login');
    toast.info('Logged out successfully');
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      toast.error('Please upload a PDF file');
      return;
    }

    uploadMutation.mutate({ file, category: pdfCategory || undefined });
  };

  const handleScrapeURL = () => {
    if (!urlToScrape) {
      toast.error('Please enter a URL');
      return;
    }

    try {
      new URL(urlToScrape);
      scrapeMutation.mutate({ url: urlToScrape, category: urlCategory || undefined });
    } catch {
      toast.error('Please enter a valid URL');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; icon: any }> = {
      completed: { variant: 'default', icon: CheckCircle2 },
      failed: { variant: 'destructive', icon: XCircle },
      processing: { variant: 'secondary', icon: RefreshCw },
      pending: { variant: 'outline', icon: Clock },
    };

    const config = variants[status] || variants.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="gap-1">
        <Icon className="w-3 h-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const stats = jobsData
    ? {
        total: jobsData.total_jobs || 0,
        completed: jobsData.completed_jobs || 0,
        failed: jobsData.failed_jobs || 0,
        pending: jobsData.pending_jobs || 0,
        processing: (jobsData.jobs || []).filter((j: any) => j.status === 'processing').length,
      }
    : { total: 0, completed: 0, failed: 0, pending: 0, processing: 0 };

  const totalQueries = 19220;
  const avgSatisfaction = 84;
  const avgResponseTime = 1.2;
  const activeAgents = 6;

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-background via-muted/10 to-background">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[#006A4E] to-[#00A86B] flex items-center justify-center shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-[#006A4E] to-[#00A86B] bg-clip-text text-transparent">
                  AfroKen LLM Admin Portal
                </h1>
                <p className="text-muted-foreground text-sm mt-1">
                  Kenya-Tuned Multilingual AI Copilot for Public Services
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="gap-1">
                <Shield className="w-3 h-3" />
                Data Protection Act 2019 Compliant
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Globe2 className="w-3 h-3" />
                47 Counties
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Languages className="w-3 h-3" />
                Swahili • English • Sheng
              </Badge>
            </div>
          </div>
          <Button variant="outline" onClick={handleLogout} className="gap-2">
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 h-12">
            <TabsTrigger value="overview" className="gap-2">
              <BarChart3 className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="documents" className="gap-2">
              <FileText className="w-4 h-4" />
              Documents
            </TabsTrigger>
            <TabsTrigger value="processing" className="gap-2">
              <Activity className="w-4 h-4" />
              Processing
            </TabsTrigger>
            <TabsTrigger value="analytics" className="gap-2">
              <TrendingUp className="w-4 h-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="models" className="gap-2">
              <Cpu className="w-4 h-4" />
              Models
            </TabsTrigger>
            <TabsTrigger value="settings" className="gap-2">
              <Settings className="w-4 h-4" />
              Settings
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="border-2 border-[#006A4E]/20 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardDescription className="text-sm font-medium">Total Citizen Queries</CardDescription>
                    <MessageSquare className="w-5 h-5 text-[#006A4E]" />
                  </div>
                  <CardTitle className="text-3xl font-bold text-[#006A4E]">{totalQueries.toLocaleString()}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <TrendingUp className="w-3 h-3 text-green-600" />
                    <span className="text-green-600 font-semibold">+12.5%</span>
                    <span>vs last month</span>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-2 border-blue-500/20 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardDescription className="text-sm font-medium">Avg. Satisfaction</CardDescription>
                    <CheckCircle className="w-5 h-5 text-blue-600" />
                  </div>
                  <CardTitle className="text-3xl font-bold text-blue-600">{avgSatisfaction}%</CardTitle>
                </CardHeader>
                <CardContent>
                  <Progress value={avgSatisfaction} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-2">Target: 85%</p>
                </CardContent>
              </Card>

              <Card className="border-2 border-purple-500/20 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardDescription className="text-sm font-medium">Avg. Response Time</CardDescription>
                    <Zap className="w-5 h-5 text-purple-600" />
                  </div>
                  <CardTitle className="text-3xl font-bold text-purple-600">{avgResponseTime}s</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <TrendingUp className="w-3 h-3 text-green-600" />
                    <span className="text-green-600 font-semibold">-8%</span>
                    <span>faster</span>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-2 border-orange-500/20 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardDescription className="text-sm font-medium">Active AI Agents</CardDescription>
                    <Server className="w-5 h-5 text-orange-600" />
                  </div>
                  <CardTitle className="text-3xl font-bold text-orange-600">{activeAgents}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Badge variant="default" className="text-xs">RAG</Badge>
                    <Badge variant="default" className="text-xs">Procedural</Badge>
                    <Badge variant="default" className="text-xs">Translation</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Channel Distribution & Language Usage */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Smartphone className="w-5 h-5 text-[#006A4E]" />
                    Citizen Access Channels
                  </CardTitle>
                  <CardDescription>Distribution across communication platforms</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={channelData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {channelData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <ChartTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    {channelData.map((channel) => (
                      <div key={channel.name} className="flex items-center gap-2 text-sm">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: channel.color }} />
                        <span className="text-muted-foreground">{channel.name}</span>
                        <span className="font-semibold ml-auto">{channel.value}%</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Languages className="w-5 h-5 text-[#006A4E]" />
                    Language Distribution
                  </CardTitle>
                  <CardDescription>Multilingual query breakdown</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {languageData.map((lang) => (
                      <div key={lang.language} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{lang.language}</span>
                          <span className="text-sm text-muted-foreground">
                            {lang.queries.toLocaleString()} queries
                          </span>
                        </div>
                        <Progress value={lang.percentage} className="h-3" />
                        <p className="text-xs text-muted-foreground">{lang.percentage}% of total</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Top Services & County Performance */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileSearch className="w-5 h-5 text-[#006A4E]" />
                    Top Service Categories
                  </CardTitle>
                  <CardDescription>Most requested government services</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {serviceData.map((service) => (
                      <div key={service.service} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{service.service}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground">
                              {service.queries.toLocaleString()} queries
                            </span>
                            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                              {service.completion}% complete
                            </Badge>
                          </div>
                        </div>
                        <Progress value={service.completion} className="h-2" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-[#006A4E]" />
                    County Performance
                  </CardTitle>
                  <CardDescription>Top 4 counties by query volume</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>County</TableHead>
                        <TableHead>Queries</TableHead>
                        <TableHead>Satisfaction</TableHead>
                        <TableHead>Escalations</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {countyData.map((county) => (
                        <TableRow key={county.name}>
                          <TableCell className="font-medium">{county.name}</TableCell>
                          <TableCell>{county.queries.toLocaleString()}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Progress value={county.satisfaction} className="w-16 h-2" />
                              <span className="text-sm">{county.satisfaction}%</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={county.escalations > 30 ? 'destructive' : 'secondary'}>
                              {county.escalations}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card className="border-2 border-[#006A4E]/30 shadow-lg bg-gradient-to-br from-[#006A4E]/5 to-transparent">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common administrative tasks</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Button
                  variant="outline"
                  className="h-24 flex-col gap-2 border-2 hover:border-[#006A4E] hover:bg-[#006A4E]/5"
                  onClick={() => setSelectedTab('documents')}
                >
                  <Upload className="w-6 h-6 text-[#006A4E]" />
                  <span className="font-semibold">Upload PDF</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-24 flex-col gap-2 border-2 hover:border-[#006A4E] hover:bg-[#006A4E]/5"
                  onClick={() => setSelectedTab('documents')}
                >
                  <Globe className="w-6 h-6 text-[#006A4E]" />
                  <span className="font-semibold">Scrape URL</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-24 flex-col gap-2 border-2 hover:border-[#006A4E] hover:bg-[#006A4E]/5"
                  onClick={() => setSelectedTab('analytics')}
                >
                  <BarChart3 className="w-6 h-6 text-[#006A4E]" />
                  <span className="font-semibold">View Reports</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-24 flex-col gap-2 border-2 hover:border-[#006A4E] hover:bg-[#006A4E]/5"
                  onClick={() => setSelectedTab('models')}
                >
                  <Settings className="w-6 h-6 text-[#006A4E]" />
                  <span className="font-semibold">System Config</span>
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents Tab - Keep existing implementation */}
          <TabsContent value="documents" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-[#006A4E]" />
                    Upload PDF Document
                  </CardTitle>
                  <CardDescription>
                    Upload a PDF file to be processed and indexed into the RAG corpus
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Category (Optional)</Label>
                    <Select value={pdfCategory} onValueChange={setPdfCategory}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ministry_faq">Ministry FAQ</SelectItem>
                        <SelectItem value="service_workflow">Service Workflow</SelectItem>
                        <SelectItem value="legal_snippet">Legal Snippet</SelectItem>
                        <SelectItem value="county_service">County Service</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pdf-upload">PDF File</Label>
                    <Input
                      ref={fileInputRef}
                      id="pdf-upload"
                      type="file"
                      accept=".pdf"
                      onChange={handleFileUpload}
                      disabled={uploadMutation.isPending}
                    />
                  </div>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full bg-[#006A4E] hover:bg-[#005a3e]"
                    disabled={uploadMutation.isPending}
                  >
                    {uploadMutation.isPending ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Select PDF File
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="w-5 h-5 text-[#006A4E]" />
                    Scrape URL
                  </CardTitle>
                  <CardDescription>
                    Scrape content from government websites and portals
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="url">URL</Label>
                    <Input
                      id="url"
                      type="url"
                      placeholder="https://www.nhif.or.ke/services"
                      value={urlToScrape}
                      onChange={(e) => setUrlToScrape(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="url-category">Category (Optional)</Label>
                    <Select value={urlCategory} onValueChange={setUrlCategory}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ministry_faq">Ministry FAQ</SelectItem>
                        <SelectItem value="service_workflow">Service Workflow</SelectItem>
                        <SelectItem value="legal_snippet">Legal Snippet</SelectItem>
                        <SelectItem value="county_service">County Service</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button
                    onClick={handleScrapeURL}
                    className="w-full bg-[#006A4E] hover:bg-[#005a3e]"
                    disabled={scrapeMutation.isPending || !urlToScrape}
                  >
                    {scrapeMutation.isPending ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Scraping...
                      </>
                    ) : (
                      <>
                        <Globe className="w-4 h-4 mr-2" />
                        Start Scraping
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Processing Tab - Keep existing but enhance styling */}
          <TabsContent value="processing" className="space-y-6">
            <Card className="border-2 shadow-lg">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Processing Jobs</CardTitle>
                    <CardDescription>
                      Monitor and manage document processing jobs
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="gap-1">
                      <Clock className="w-3 h-3" />
                      {stats.pending} Pending
                    </Badge>
                    <Badge variant="secondary" className="gap-1">
                      <RefreshCw className="w-3 h-3" />
                      {stats.processing} Processing
                    </Badge>
                    <Badge variant="default" className="gap-1 bg-green-600">
                      <CheckCircle2 className="w-3 h-3" />
                      {stats.completed} Completed
                    </Badge>
                    {stats.failed > 0 && (
                      <Badge variant="destructive" className="gap-1">
                        <XCircle className="w-3 h-3" />
                        {stats.failed} Failed
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {selectedJobs.size > 0 && (
                  <div className="mb-4 flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm font-medium">
                      {selectedJobs.size} job(s) selected
                    </span>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={handleDeleteSelected}
                      disabled={deleteJobsMutation.isPending}
                    >
                      {deleteJobsMutation.isPending ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete Selected
                        </>
                      )}
                    </Button>
                  </div>
                )}
                {jobsLoading ? (
                  <div className="text-center py-8 text-muted-foreground">Loading jobs...</div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">
                          <Checkbox
                            checked={selectedJobs.size > 0 && selectedJobs.size === jobsData?.jobs?.length}
                            onCheckedChange={handleSelectAll}
                          />
                        </TableHead>
                        <TableHead>Job ID</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Source</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Progress</TableHead>
                        <TableHead>Documents</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {jobsData?.jobs && jobsData.jobs.length > 0 ? (
                        jobsData.jobs.map((job: any) => (
                          <TableRow key={job.job_id}>
                            <TableCell>
                              <Checkbox
                                checked={selectedJobs.has(job.job_id)}
                                onCheckedChange={() => handleSelectJob(job.job_id)}
                              />
                            </TableCell>
                            <TableCell className="font-mono text-xs">
                              {job.job_id.substring(0, 8)}...
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline">
                                {job.job_type === 'pdf_upload' ? (
                                  <FileText className="w-3 h-3 mr-1" />
                                ) : (
                                  <LinkIcon className="w-3 h-3 mr-1" />
                                )}
                                {job.job_type.replace('_', ' ')}
                              </Badge>
                            </TableCell>
                            <TableCell className="max-w-xs truncate" title={job.source}>
                              {job.source}
                            </TableCell>
                            <TableCell>{getStatusBadge(job.status)}</TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <Progress value={job.progress} className="w-20" />
                                <span className="text-xs">{job.progress}%</span>
                              </div>
                            </TableCell>
                            <TableCell>{job.documents_processed || 0}</TableCell>
                            <TableCell>
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => setSelectedJob(job.job_id)}
                                  >
                                    <Eye className="w-4 h-4" />
                                  </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-2xl">
                                  <DialogHeader>
                                    <DialogTitle>Job Details</DialogTitle>
                                    <DialogDescription>
                                      {job.job_id}
                                    </DialogDescription>
                                  </DialogHeader>
                                  {jobStatus && (
                                    <div className="space-y-4">
                                      <div>
                                        <Label>Status</Label>
                                        <div className="mt-1">{getStatusBadge(jobStatus.status)}</div>
                                      </div>
                                      <div>
                                        <Label>Progress</Label>
                                        <Progress value={jobStatus.progress} className="mt-1" />
                                      </div>
                                      {jobStatus.error_message && (
                                        <div className="p-3 bg-red-50 dark:bg-red-950 rounded-md">
                                          <p className="text-sm text-red-900 dark:text-red-100">
                                            {jobStatus.error_message}
                                          </p>
                                        </div>
                                      )}
                                      {jobStatus.result && (
                                        <div className="p-3 bg-green-50 dark:bg-green-950 rounded-md">
                                          <pre className="text-xs overflow-auto">
                                            {JSON.stringify(jobStatus.result, null, 2)}
                                          </pre>
                                        </div>
                                      )}
                                    </div>
                                  )}
                              </DialogContent>
                              </Dialog>
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                            No processing jobs found
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                )}
                <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                      <AlertDialogDescription>
                        You are about to delete {selectedJobs.size} job(s). This action cannot be undone.
                        {selectedJobs.size === 1 && jobsData?.jobs?.find((j: any) => selectedJobs.has(j.job_id)) && (
                          <span className="block mt-2 text-sm font-medium">
                            Job: {jobsData.jobs.find((j: any) => selectedJobs.has(j.job_id))?.source}
                          </span>
                        )}
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={confirmDelete}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab - New comprehensive analytics */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle>Query Trends</CardTitle>
                  <CardDescription>Last 30 days query volume</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={[
                      { day: 'Week 1', queries: 4200 },
                      { day: 'Week 2', queries: 4800 },
                      { day: 'Week 3', queries: 5200 },
                      { day: 'Week 4', queries: 5020 },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <ChartTooltip />
                      <Line type="monotone" dataKey="queries" stroke="#006A4E" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle>Service Completion Rates</CardTitle>
                  <CardDescription>Success rate by service category</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={serviceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="service" />
                      <YAxis />
                      <ChartTooltip />
                      <Bar dataKey="completion" fill="#006A4E" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            <Card className="border-2 shadow-lg">
              <CardHeader>
                <CardTitle>County-Level Analytics</CardTitle>
                <CardDescription>Select a county to view detailed metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <Select value={selectedCounty} onValueChange={setSelectedCounty}>
                    <SelectTrigger className="w-64">
                      <SelectValue placeholder="Select county" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Counties</SelectItem>
                      {countyData.map((county) => (
                        <SelectItem key={county.name} value={county.name}>
                          {county.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>County</TableHead>
                      <TableHead>Total Queries</TableHead>
                      <TableHead>Satisfaction Rate</TableHead>
                      <TableHead>Avg Response Time</TableHead>
                      <TableHead>Escalations</TableHead>
                      <TableHead>Top Service</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {countyData.map((county) => (
                      <TableRow key={county.name}>
                        <TableCell className="font-medium">{county.name}</TableCell>
                        <TableCell>{county.queries.toLocaleString()}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={county.satisfaction} className="w-20 h-2" />
                            <span>{county.satisfaction}%</span>
                          </div>
                        </TableCell>
                        <TableCell>1.3s</TableCell>
                        <TableCell>
                          <Badge variant={county.escalations > 30 ? 'destructive' : 'secondary'}>
                            {county.escalations}
                          </Badge>
                        </TableCell>
                        <TableCell>NHIF</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Models Tab - Enhanced with more details */}
          <TabsContent value="models" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-[#006A4E]" />
                    LLM Configuration
                  </CardTitle>
                  <CardDescription>
                    Fine-tuned Mistral/LLaMA-3 7B model settings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fine-tuned-endpoint">Fine-Tuned LLM Endpoint</Label>
                    <Input
                      id="fine-tuned-endpoint"
                      placeholder="http://localhost:8000/v1/chat/completions"
                      value={modelSettings.fineTunedEndpoint}
                      onChange={(e) =>
                        setModelSettings({ ...modelSettings, fineTunedEndpoint: e.target.value })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Mistral/LLaMA-3 7B fine-tuned via LoRA
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="llm-endpoint">Generic LLM Endpoint (Fallback)</Label>
                    <Input
                      id="llm-endpoint"
                      placeholder="http://localhost:8000/generate"
                      value={modelSettings.llmEndpoint}
                      onChange={(e) =>
                        setModelSettings({ ...modelSettings, llmEndpoint: e.target.value })
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div>
                      <Label>Model Status</Label>
                      <p className="text-xs text-muted-foreground">Fine-tuned model active</p>
                    </div>
                    <Badge variant="default" className="bg-green-600">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Online
                    </Badge>
                  </div>
                  <Button className="w-full bg-[#006A4E] hover:bg-[#005a3e]">Save LLM Settings</Button>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-[#006A4E]" />
                    Embedding Configuration
                  </CardTitle>
                  <CardDescription>
                    Sentence Transformers for RAG retrieval
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="embedding-endpoint">Embedding Endpoint</Label>
                    <Input
                      id="embedding-endpoint"
                      placeholder="http://localhost:8000/embeddings"
                      value={modelSettings.embeddingEndpoint}
                      onChange={(e) =>
                        setModelSettings({ ...modelSettings, embeddingEndpoint: e.target.value })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Leave empty to use local all-MiniLM-L6-v2 (384-dim)
                    </p>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div>
                      <Label>Current Model</Label>
                      <p className="text-xs text-muted-foreground">all-MiniLM-L6-v2</p>
                    </div>
                    <Badge variant="default" className="bg-green-600">
                      Active
                    </Badge>
                  </div>
                  <Button className="w-full bg-[#006A4E] hover:bg-[#005a3e]">Save Embedding Settings</Button>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mic className="w-5 h-5 text-[#006A4E]" />
                    Audio Processing
                  </CardTitle>
                  <CardDescription>
                    Whisper ASR + Coqui TTS for voice interfaces
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-3">
                      <Mic className="w-5 h-5 text-[#006A4E]" />
                      <div>
                        <Label>Whisper ASR</Label>
                        <p className="text-xs text-muted-foreground">Speech-to-text (Kenyan accents)</p>
                      </div>
                    </div>
                    <Switch
                      checked={modelSettings.whisperEnabled}
                      onCheckedChange={(checked) =>
                        setModelSettings({ ...modelSettings, whisperEnabled: checked })
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-3">
                      <Volume2 className="w-5 h-5 text-[#006A4E]" />
                      <div>
                        <Label>Coqui TTS</Label>
                        <p className="text-xs text-muted-foreground">Text-to-speech (Swahili/English)</p>
                      </div>
                    </div>
                    <Switch
                      checked={modelSettings.ttsEnabled}
                      onCheckedChange={(checked) =>
                        setModelSettings({ ...modelSettings, ttsEnabled: checked })
                      }
                    />
                  </div>
                  <Button className="w-full bg-[#006A4E] hover:bg-[#005a3e]">Save Audio Settings</Button>
                </CardContent>
              </Card>

              <Card className="border-2 shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="w-5 h-5 text-[#006A4E]" />
                    Storage Configuration
                  </CardTitle>
                  <CardDescription>
                    PostgreSQL + pgvector & MinIO object storage
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div>
                      <Label>PostgreSQL + pgvector</Label>
                      <p className="text-xs text-muted-foreground">Vector database for RAG</p>
                    </div>
                    <Switch
                      checked={modelSettings.usePostgreSQL}
                      onCheckedChange={(checked) =>
                        setModelSettings({ ...modelSettings, usePostgreSQL: checked })
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div>
                      <Label>MinIO Object Storage</Label>
                      <p className="text-xs text-muted-foreground">Document & audio storage</p>
                    </div>
                    <Switch
                      checked={modelSettings.useMinIO}
                      onCheckedChange={(checked) =>
                        setModelSettings({ ...modelSettings, useMinIO: checked })
                      }
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div>
                      <Label>FAISS Index</Label>
                      <p className="text-xs text-muted-foreground">Local vector index (fallback)</p>
                    </div>
                    <Badge variant="default" className="bg-green-600">
                      Active
                    </Badge>
                  </div>
                  <Button className="w-full bg-[#006A4E] hover:bg-[#005a3e]">Save Storage Settings</Button>
                </CardContent>
              </Card>
            </div>

            {/* Agent Status */}
            <Card className="border-2 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="w-5 h-5 text-[#006A4E]" />
                  AI Agent Status
                </CardTitle>
                <CardDescription>
                  Monitor agentic workflow engine components
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { name: 'Intent Agent', status: 'active', description: 'Classifies user requests' },
                    { name: 'RAG Agent', status: 'active', description: 'Retrieves verified documents' },
                    { name: 'Procedural Agent', status: 'active', description: 'Generates step-by-step workflows' },
                    { name: 'Translation Agent', status: 'active', description: 'Swahili/Sheng/English' },
                    { name: 'API Tool Agent', status: 'active', description: 'Books appointments, checks status' },
                    { name: 'Escalation Agent', status: 'active', description: 'Hands over to human officers' },
                  ].map((agent) => (
                    <div key={agent.name} className="p-4 border rounded-lg flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{agent.name}</p>
                        <p className="text-xs text-muted-foreground">{agent.description}</p>
                      </div>
                      <Badge variant="default" className="bg-green-600">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        {agent.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            {/* Add Service Form */}
            <Card className="border-2 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileCheck className="w-5 h-5 text-[#006A4E]" />
                  Add New Service
                </CardTitle>
                <CardDescription>
                  Add a new government service that will appear as a card on the Services page
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="service-title">Service Title *</Label>
                  <Input
                    id="service-title"
                    placeholder="e.g., NTSA Services"
                    value={newService.title}
                    onChange={(e) => setNewService({ ...newService, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="service-description">Description *</Label>
                  <Textarea
                    id="service-description"
                    placeholder="Brief description of the service"
                    value={newService.description}
                    onChange={(e) => setNewService({ ...newService, description: e.target.value })}
                    rows={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="service-category">Category</Label>
                  <Select value={newService.category} onValueChange={(value) => setNewService({ ...newService, category: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">General</SelectItem>
                      <SelectItem value="health">Health</SelectItem>
                      <SelectItem value="finance">Finance</SelectItem>
                      <SelectItem value="identity">Identity</SelectItem>
                      <SelectItem value="business">Business</SelectItem>
                      <SelectItem value="travel">Travel</SelectItem>
                      <SelectItem value="transport">Transport</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="service-logo">Service Logo (Optional)</Label>
                  <Input
                    id="service-logo"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setNewService({ ...newService, logo: e.target.files?.[0] || null })}
                  />
                  <p className="text-xs text-muted-foreground">Upload a logo image for the service card</p>
                </div>
                <Button 
                  className="w-full bg-[#006A4E] hover:bg-[#005a3e]"
                  onClick={() => {
                    if (!newService.title || !newService.description) {
                      toast.error('Please fill in title and description');
                      return;
                    }
                    serviceMutation.mutate();
                  }}
                  disabled={serviceMutation.isPending}
                >
                  {serviceMutation.isPending ? 'Creating...' : 'Add Service'}
                </Button>
              </CardContent>
            </Card>

            {/* Add Huduma Centre Form */}
            <Card className="border-2 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-[#006A4E]" />
                  Add New Huduma Centre
                </CardTitle>
                <CardDescription>
                  Add a new Huduma Centre location to the database
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="huduma-name">Centre Name *</Label>
                    <Input
                      id="huduma-name"
                      placeholder="e.g., Huduma Centre Nairobi West"
                      value={newHuduma.name}
                      onChange={(e) => setNewHuduma({ ...newHuduma, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-county">County *</Label>
                    <Input
                      id="huduma-county"
                      placeholder="e.g., Nairobi"
                      value={newHuduma.county}
                      onChange={(e) => setNewHuduma({ ...newHuduma, county: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-sub-county">Sub-County</Label>
                    <Input
                      id="huduma-sub-county"
                      placeholder="e.g., Westlands"
                      value={newHuduma.sub_county}
                      onChange={(e) => setNewHuduma({ ...newHuduma, sub_county: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-town">Town</Label>
                    <Input
                      id="huduma-town"
                      placeholder="e.g., Westlands"
                      value={newHuduma.town}
                      onChange={(e) => setNewHuduma({ ...newHuduma, town: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-latitude">Latitude</Label>
                    <Input
                      id="huduma-latitude"
                      type="number"
                      step="any"
                      placeholder="e.g., -1.2921"
                      value={newHuduma.latitude}
                      onChange={(e) => setNewHuduma({ ...newHuduma, latitude: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-longitude">Longitude</Label>
                    <Input
                      id="huduma-longitude"
                      type="number"
                      step="any"
                      placeholder="e.g., 36.8219"
                      value={newHuduma.longitude}
                      onChange={(e) => setNewHuduma({ ...newHuduma, longitude: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-phone">Contact Phone</Label>
                    <Input
                      id="huduma-phone"
                      placeholder="+254 20 2222222"
                      value={newHuduma.contact_phone}
                      onChange={(e) => setNewHuduma({ ...newHuduma, contact_phone: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="huduma-email">Contact Email</Label>
                    <Input
                      id="huduma-email"
                      type="email"
                      placeholder="centre@hudumakenya.go.ke"
                      value={newHuduma.contact_email}
                      onChange={(e) => setNewHuduma({ ...newHuduma, contact_email: e.target.value })}
                    />
                  </div>
                </div>
                <Button 
                  className="w-full bg-[#006A4E] hover:bg-[#005a3e]"
                  onClick={() => {
                    if (!newHuduma.name || !newHuduma.county) {
                      toast.error('Please fill in name and county');
                      return;
                    }
                    hudumaMutation.mutate();
                  }}
                  disabled={hudumaMutation.isPending}
                >
                  {hudumaMutation.isPending ? 'Creating...' : 'Add Huduma Centre'}
                </Button>
              </CardContent>
            </Card>

            {/* System Settings */}
            <Card className="border-2 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5 text-[#006A4E]" />
                  System Settings
                </CardTitle>
                <CardDescription>
                  General system configuration and compliance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>API Base URL</Label>
                  <Input
                    defaultValue={API_BASE_URL}
                    placeholder="http://localhost:8000"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Environment</Label>
                  <Select defaultValue="development">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="development">Development</SelectItem>
                      <SelectItem value="staging">Staging</SelectItem>
                      <SelectItem value="production">Production</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="p-4 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-amber-600 mt-0.5" />
                    <div>
                      <p className="font-semibold text-amber-900 dark:text-amber-100">Compliance Status</p>
                      <p className="text-sm text-amber-800 dark:text-amber-200 mt-1">
                        System complies with Kenya Data Protection Act 2019, Digital Government Guidelines, and UNESCO AI Ethics Guidelines.
                      </p>
                    </div>
                  </div>
                </div>
                <Button className="w-full bg-[#006A4E] hover:bg-[#005a3e]">Save Settings</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
