import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { MessageSquare, Shield, Globe2 } from 'lucide-react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { ServiceCard } from '@/components/ServiceCard';
import { ChatWindow } from '@/components/Chat/ChatWindow';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { SERVICES } from '@/constants/services';
import { useChatStore } from '@/store/chatStore';
import heroBackground from '@/assets/hero-background.jpg';

export default function Index() {
  const { t } = useTranslation();
  const { setIsOpen, setCurrentService } = useChatStore();

  const handleStartChat = (serviceId?: string) => {
    if (serviceId) {
      setCurrentService(serviceId as any);
    }
    setIsOpen(true);
  };

  const features = [
    {
      icon: MessageSquare,
      title: t('home.features.instant.title'),
      description: t('home.features.instant.description'),
    },
    {
      icon: Shield,
      title: t('home.features.verified.title'),
      description: t('home.features.verified.description'),
    },
    {
      icon: Globe2,
      title: t('home.features.multilingual.title'),
      description: t('home.features.multilingual.description'),
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative overflow-hidden">
          {/* Hero Background Image */}
          <div 
            className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-60"
            style={{ backgroundImage: `url(${heroBackground})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-background/95 via-background/90 to-primary/20" />
          
          <div className="container mx-auto px-4 py-24 md:py-40 relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center max-w-4xl mx-auto"
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="inline-block mb-6 px-4 py-2 rounded-full glass-effect"
              >
                <span className="text-sm font-medium text-primary">
                  🇰🇪 Powered by AI • Multilingual • Accessible
                </span>
              </motion.div>
              
              <h1 className="text-5xl md:text-7xl font-display font-bold mb-6 leading-tight">
                <span className="text-gradient">{t('home.hero.title')}</span>
              </h1>
              
              <p className="text-xl md:text-2xl text-muted-foreground mb-10 leading-relaxed">
                {t('home.hero.subtitle')}
              </p>
              
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <Button
                  size="lg"
                  onClick={() => handleStartChat()}
                  className="gap-2 text-lg px-10 py-6 shadow-glow hover-lift focus-ring font-semibold"
                >
                  <MessageSquare className="w-6 h-6" aria-hidden="true" />
                  {t('home.hero.cta')}
                </Button>
              </motion.div>
            </motion.div>
          </div>
          
          {/* Decorative elements */}
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        </section>

        {/* Services Section */}
        <section className="container mx-auto px-4 py-20 md:py-24">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-4">
              {t('home.services.title')}
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Select a service to get started with personalized assistance
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {SERVICES.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                whileHover={{ scale: 1.02 }}
              >
                <ServiceCard
                  service={service}
                  onClick={() => handleStartChat(service.id)}
                />
              </motion.div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 md:py-24 bg-muted/30">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-display font-bold mb-4">
                {t('home.features.title')}
              </h2>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Designed with accessibility and ease of use in mind
              </p>
            </motion.div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.15 }}
                >
                  <Card className="h-full smooth-transition hover-lift group relative overflow-hidden border-2">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <CardContent className="p-8 relative">
                      <div
                        className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 group-hover:shadow-glow transition-all duration-300"
                        aria-hidden="true"
                      >
                        <feature.icon className="w-7 h-7 text-primary" />
                      </div>
                      <h3 className="font-display font-semibold text-xl mb-3 group-hover:text-primary transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 md:py-24 relative overflow-hidden">
          <div className="absolute inset-0 gradient-primary opacity-10" />
          <div className="container mx-auto px-4 relative">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="max-w-3xl mx-auto text-center"
            >
              <h2 className="text-4xl md:text-5xl font-display font-bold mb-6">
                Ready to get started?
              </h2>
              <p className="text-xl text-muted-foreground mb-10 leading-relaxed">
                Ask any question about government services and get instant, verified answers
              </p>
              <Button
                size="lg"
                onClick={() => handleStartChat()}
                className="text-lg px-10 py-6 focus-ring shadow-glow hover-lift font-semibold"
              >
                Start Conversation Now
              </Button>
            </motion.div>
          </div>
        </section>
      </main>

      <Footer />
      <ChatWindow />
    </div>
  );
}
