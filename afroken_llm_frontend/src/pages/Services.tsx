import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import {
  Search,
  Heart,
  CreditCard,
  ShieldCheck,
  Briefcase,
  FileText,
  Plane,
  Users,
  Building2,
  Wallet,
  ExternalLink,
} from 'lucide-react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { ChatWindow } from '@/components/Chat/ChatWindow';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useChatStore } from '@/store/chatStore';

interface Service {
  id: string;
  title: string;
  description: string;
  icon: any;
  iconBg: string;
  iconColor: string;
  category: string[];
  popular?: boolean;
  logo?: string;
  portalUrl?: string;
}

const ALL_SERVICES: Service[] = [
  {
    id: 'nhif',
    title: 'NHIF Health Insurance',
    description: 'Check status, renew membership, and get coverage information',
    icon: Heart,
    iconBg: 'bg-red-50',
    iconColor: 'text-red-600',
    category: ['all', 'health'],
    popular: true,
    logo: '/logos/NHIF-logo.jpg',
  },
  {
    id: 'kra',
    title: 'KRA Tax Services',
    description: 'File returns, get PIN, check compliance status',
    icon: CreditCard,
    iconBg: 'bg-emerald-50',
    iconColor: 'text-emerald-600',
    category: ['all', 'finance'],
    popular: true,
    logo: '/logos/kra_logo.png',
  },
  {
    id: 'national-id',
    title: 'National ID',
    description: 'Apply for new ID, replacement, or check application status',
    icon: ShieldCheck,
    iconBg: 'bg-blue-50',
    iconColor: 'text-blue-600',
    category: ['all', 'identity'],
    popular: true,
    logo: '/logos/coa-republic-of-kenya.png',
  },
  {
    id: 'business',
    title: 'Business Registration',
    description: 'Register business name, get permits and licenses',
    icon: Briefcase,
    iconBg: 'bg-purple-50',
    iconColor: 'text-purple-600',
    category: ['all', 'business'],
    popular: true,
    logo: '/logos/agency-business-registration-services.png',
  },
  {
    id: 'birth-certificate',
    title: 'Birth Certificate',
    description: 'Apply for birth certificate, replacement, corrections',
    icon: FileText,
    iconBg: 'bg-orange-50',
    iconColor: 'text-orange-600',
    category: ['all', 'identity'],
    logo: '/logos/coa-republic-of-kenya.png',
  },
  {
    id: 'passport',
    title: 'Passport Services',
    description: 'Apply for new passport, renewal, tracking',
    icon: Plane,
    iconBg: 'bg-indigo-50',
    iconColor: 'text-indigo-600',
    category: ['all', 'travel', 'identity'],
    logo: '/logos/agency-directorate-of-immigration-services.png',
  },
  {
    id: 'huduma',
    title: 'Huduma Number',
    description: 'Register for Huduma Number and manage services',
    icon: Users,
    iconBg: 'bg-teal-50',
    iconColor: 'text-teal-600',
    category: ['all', 'identity'],
    logo: '/logos/huduma center logo.png',
  },
  {
    id: 'nssf',
    title: 'NSSF Pension',
    description: 'Check contributions, register, claim benefits',
    icon: Wallet,
    iconBg: 'bg-cyan-50',
    iconColor: 'text-cyan-600',
    category: ['all', 'finance'],
    logo: '/logos/agency-boma-yangu.png',
  },
  {
    id: 'county-mombasa',
    title: '001 - Mombasa County',
    description: 'County services including rates, business permits and local programmes.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-mombasa.png',
  },
  {
    id: 'county-meru',
    title: '012 - Meru County',
    description: 'Access Meru County online services and citizen support.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-meru.png',
  },
  {
    id: 'county-tharaka-nithi',
    title: '013 - Tharaka-Nithi County',
    description: 'County government information and e-services.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-tharaka-nithi.png',
  },
  {
    id: 'county-embu',
    title: '014 - Embu County',
    description: 'Explore Embu County services, permits and development programmes.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-embu.png',
  },
  {
    id: 'county-kajiado',
    title: '034 - Kajiado County',
    description: 'Land, trade licences and local administration services.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-kajiado.png',
  },
  {
    id: 'county-bomet',
    title: '036 - Bomet County',
    description: 'Access Bomet County digital services and citizen support.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-bomet.png',
  },
  {
    id: 'county-kisumu',
    title: '042 - Kisumu County',
    description: 'County portal for Kisumu services, rates and programmes.',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
    logo: '/logos/county-emblem-kisumu-e1685409314140.png',
  },
];

const CATEGORIES = [
  { id: 'all', label: 'All Services' },
  { id: 'health', label: 'Health' },
  { id: 'finance', label: 'Finance' },
  { id: 'identity', label: 'Identity' },
  { id: 'business', label: 'Business' },
  { id: 'travel', label: 'Travel' },
  { id: 'local-government', label: 'Local Government' },
];

export default function Services() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { setIsOpen, setCurrentService } = useChatStore();
  const shouldReduceMotion = useReducedMotion();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');

  const handleGetHelp = (serviceId: string) => {
    setCurrentService(serviceId as any);
    setIsOpen(true);
  };

  const filteredServices = ALL_SERVICES.filter((service) => {
    const matchesCategory = service.category.includes(activeCategory);
    const matchesSearch = 
      service.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="relative flex-1 overflow-hidden">
        {/* Animated Kenya flag video background */}
        <video
          className="pointer-events-none absolute inset-0 -z-10 h-full w-full object-cover opacity-50"
          autoPlay
          loop
          muted
          playsInline
          aria-hidden="true"
        >
          <source src="/animated_flag/kenya-flag.webm" type="video/webm" />
        </video>
        {/* Overlay for content readability */}
        <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-background/50 via-background/40 to-background/50" aria-hidden="true" />
        
        <div className="relative container mx-auto px-4 py-12">
          {/* Header Section */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
            animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: 'easeOut' }}
            className="mb-12 text-center"
          >
            <h1 className="text-4xl md:text-5xl font-display font-bold mb-4 text-gradient">
              Government Services
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Browse all available services or search for what you need
            </p>
          </motion.div>

          {/* Search Bar */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
            animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: 'easeOut', delay: 0.1 }}
            className="mx-auto mb-8 max-w-2xl"
          >
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search services... (e.g., NHIF, tax, ID)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 py-6 text-base focus-ring shadow-md"
                aria-label="Search services"
              />
            </div>
          </motion.div>

          {/* Category Filter */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
            animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: 'easeOut', delay: 0.2 }}
            className="mb-12 flex flex-wrap justify-center gap-2"
          >
            {CATEGORIES.map((category) => (
              <Button
                key={category.id}
                variant={activeCategory === category.id ? 'default' : 'outline'}
                onClick={() => setActiveCategory(category.id)}
                className={`focus-ring ${
                  activeCategory === category.id 
                    ? 'shadow-md' 
                    : 'hover:bg-primary/5'
                }`}
              >
                {category.label}
              </Button>
            ))}
          </motion.div>

          {/* Services Grid */}
          <div className="mx-auto grid max-w-4xl grid-cols-1 gap-5 md:grid-cols-2">
            {filteredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={shouldReduceMotion ? false : { opacity: 0, y: 30 }}
                animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
                transition={{ duration: 0.35, ease: 'easeOut', delay: index * 0.05 }}
              >
                <Card className="group h-full border-2 bg-card/90 shadow-sm transition-all duration-300 hover:border-primary/50 hover:shadow-glow relative overflow-hidden">
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/8 via-transparent to-accent/10 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                  <CardContent className="relative flex flex-col gap-4 p-4">
                    <div className="flex items-start gap-3">
                      {/* Logo */}
                      <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-md border bg-white p-1">
                        {service.logo ? (
                          <img
                            src={service.logo}
                            alt={service.title}
                            className="h-10 w-10 object-contain"
                          />
                        ) : (
                          <service.icon className={`h-6 w-6 ${service.iconColor}`} />
                        )}
                      </div>

                      <div className="flex-1">
                        <h3 className="mb-1 font-display text-base font-semibold text-foreground group-hover:text-primary">
                          {service.title}
                        </h3>
                        <p className="text-xs leading-relaxed text-muted-foreground">
                          {service.description}
                        </p>
                      </div>
                    </div>

                    <div className="mt-1 flex items-center justify-between gap-2">
                      <Button
                        onClick={() => handleGetHelp(service.id)}
                        className="flex-1 text-xs font-semibold focus-ring"
                        size="sm"
                        variant="outline"
                      >
                        Get help with this service
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* No Results */}
          {filteredServices.length === 0 && (
            <motion.div
              initial={shouldReduceMotion ? false : { opacity: 0 }}
              animate={shouldReduceMotion ? undefined : { opacity: 1 }}
              className="py-12 text-center"
            >
              <p className="text-lg text-muted-foreground">
                No services found matching your search. Try a different keyword.
              </p>
            </motion.div>
          )}

          {/* Additional grouped sections (e.g. Health, Identity, Finance) can be added here if needed */}
        </div>
      </main>

      <Footer />
      <ChatWindow />
    </div>
  );
}
