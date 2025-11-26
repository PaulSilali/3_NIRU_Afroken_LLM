import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Heart, CreditCard, ShieldCheck, Briefcase, FileText, Plane, Users, Building2, Wallet } from 'lucide-react';
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
  },
  {
    id: 'birth-certificate',
    title: 'Birth Certificate',
    description: 'Apply for birth certificate, replacement, corrections',
    icon: FileText,
    iconBg: 'bg-orange-50',
    iconColor: 'text-orange-600',
    category: ['all', 'identity'],
  },
  {
    id: 'passport',
    title: 'Passport Services',
    description: 'Apply for new passport, renewal, tracking',
    icon: Plane,
    iconBg: 'bg-indigo-50',
    iconColor: 'text-indigo-600',
    category: ['all', 'travel', 'identity'],
  },
  {
    id: 'huduma',
    title: 'Huduma Number',
    description: 'Register for Huduma Number and manage services',
    icon: Users,
    iconBg: 'bg-teal-50',
    iconColor: 'text-teal-600',
    category: ['all', 'identity'],
  },
  {
    id: 'nssf',
    title: 'NSSF Pension',
    description: 'Check contributions, register, claim benefits',
    icon: Wallet,
    iconBg: 'bg-cyan-50',
    iconColor: 'text-cyan-600',
    category: ['all', 'finance'],
  },
  {
    id: 'county',
    title: 'County Services',
    description: 'Land rates, business permits, county-specific services',
    icon: Building2,
    iconBg: 'bg-amber-50',
    iconColor: 'text-amber-600',
    category: ['all', 'local-government'],
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
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');

  const handleGetHelp = (serviceId: string) => {
    setCurrentService(serviceId as any);
    setIsOpen(true);
    // Scroll to top to show chat
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
      
      <main className="flex-1 bg-gradient-hero">
        <div className="container mx-auto px-4 py-12">
          {/* Header Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
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
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="max-w-2xl mx-auto mb-8"
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
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-wrap gap-2 justify-center mb-12"
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {filteredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
              >
                <Card className="h-full border-2 shadow-lg hover-lift smooth-transition group">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4 mb-4">
                      {/* Icon */}
                      <div className={`w-14 h-14 rounded-xl ${service.iconBg} flex items-center justify-center flex-shrink-0 group-hover:shadow-md transition-shadow`}>
                        <service.icon className={`w-7 h-7 ${service.iconColor}`} />
                      </div>

                      {/* Popular Badge */}
                      {service.popular && (
                        <Badge className="bg-teal-600 hover:bg-teal-700 text-white ml-auto">
                          Popular
                        </Badge>
                      )}
                    </div>

                    {/* Title */}
                    <h3 className="font-display font-bold text-xl mb-2 group-hover:text-primary transition-colors">
                      {service.title}
                    </h3>

                    {/* Description */}
                    <p className="text-muted-foreground text-sm mb-6 leading-relaxed">
                      {service.description}
                    </p>

                    {/* Get Help Button */}
                    <Button
                      onClick={() => handleGetHelp(service.id)}
                      className={`w-full focus-ring ${
                        service.popular 
                          ? 'bg-emerald-700 hover:bg-emerald-800 text-white shadow-md' 
                          : 'bg-white hover:bg-gray-50 text-foreground border-2'
                      }`}
                      variant={service.popular ? 'default' : 'outline'}
                    >
                      Get Help
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* No Results */}
          {filteredServices.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <p className="text-muted-foreground text-lg">
                No services found matching your search. Try a different keyword.
              </p>
            </motion.div>
          )}
        </div>
      </main>

      <Footer />
      <ChatWindow />
    </div>
  );
}
